from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.utils.html import format_html
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta

# Import your own models only once
from .models import (
    User, PlantCategory, Product, Order, OrderItem,
    Notification, Address, AddToCart, Contact, OrderStatusHistory,
    Home, Review, 
)

# =====================================================
# 🧭 Admin Panel Customization
# =====================================================
admin.site.site_header = "Fernshub Admin"
admin.site.site_title = "Fernshub Management Panel"
admin.site.index_title = "Manage Users, Orders, and Products"

# =====================================================
# Order Status History Inline
# =====================================================
class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['created_at', 'status', 'note']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False

# =====================================================
# 🧾 Inline: Order Items inside Order with Stock Tracking
# =====================================================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ("display_total_price", "product_stock_status", "item_revenue", "stock_impact", "current_stock_level")
    max_num = 20

    def display_total_price(self, obj):
        return f"₹{obj.total_price}" if obj.id else "Save order first"
    display_total_price.short_description = "Total Price (₹)"

    def product_stock_status(self, obj):
        if obj.product:
            available = obj.product.stock_quantity - obj.product.sold_quantity
            if available <= 0:
                return format_html('<span style="color: red; font-weight: bold;">🔴 Out of Stock</span>')
            elif available <= 5:
                return format_html('<span style="color: orange; font-weight: bold;">🟡 Low ({})</span>', available)
            elif available <= 15:
                return format_html('<span style="color: blue; font-weight: bold;">🔵 Medium ({})</span>', available)
            else:
                return format_html('<span style="color: green; font-weight: bold;">🟢 Good ({})</span>', available)
        return "N/A"
    product_stock_status.short_description = "Current Stock"

    def current_stock_level(self, obj):
        if obj.product:
            available = obj.product.stock_quantity - obj.product.sold_quantity
            return f"{available} units available"
        return "N/A"
    current_stock_level.short_description = "Available Stock"

    def item_revenue(self, obj):
        return f"₹{obj.total_price}" if obj.id else "N/A"
    item_revenue.short_description = "Revenue"

    def stock_impact(self, obj):
        if obj.id and obj.product:
            current_stock = obj.product.stock_quantity - obj.product.sold_quantity
            after_stock = current_stock - obj.quantity
            
            if after_stock < 0:
                return format_html(
                    '<span style="color: red; font-weight: bold;">❌ OVERSTOCK by {} units</span><br>'
                    '<small>Current: {}, After: {}</small>', 
                    abs(after_stock), current_stock, after_stock
                )
            elif after_stock == 0:
                return format_html(
                    '<span style="color: orange; font-weight: bold;">⚠️ WILL BE OUT OF STOCK</span><br>'
                    '<small>Current: {}, After: {}</small>', 
                    current_stock, after_stock
                )
            elif after_stock <= 5:
                return format_html(
                    '<span style="color: orange;">📉 LOW STOCK AFTER</span><br>'
                    '<small>Current: {}, After: {}</small>', 
                    current_stock, after_stock
                )
            else:
                return format_html(
                    '<span style="color: green;">✅ STOCK OK AFTER</span><br>'
                    '<small>Current: {}, After: {}</small>', 
                    current_stock, after_stock
                )
        return "Calculate after save"
    stock_impact.short_description = "Stock Impact"

# =====================================================
# 👤 User Admin with Order Analytics
# =====================================================
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "contact", "points", "total_orders", "total_spent", "last_order_date", "date_joined")
    search_fields = ("username", "email", "contact")
    ordering = ["username"]
    list_per_page = 20
    readonly_fields = ("date_joined", "last_login", "total_orders", "total_spent", "last_order_date")
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'contact', 'points')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def total_orders(self, obj):
        return obj.orders.count()
    total_orders.short_description = "Total Orders"

    def total_spent(self, obj):
        total = obj.orders.aggregate(total=Sum('total_price'))['total'] or 0
        return f"₹{total:.2f}"
    total_spent.short_description = "Total Spent"

    def last_order_date(self, obj):
        last_order = obj.orders.order_by('-created_at').first()
        return last_order.created_at if last_order else "No orders"
    last_order_date.short_description = "Last Order"

# =====================================================
# 🌿 Plant Category Admin with Sales Analytics
# =====================================================
@admin.register(PlantCategory)
class PlantCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "product_count", "total_sales", "popularity_score", "stock_health")
    search_fields = ("name", "slug")
    ordering = ["name"]
    list_per_page = 20
    prepopulated_fields = {"slug": ("name",)}

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Products"

    def total_sales(self, obj):
        total_sales = OrderItem.objects.filter(
            product__category=obj
        ).aggregate(total=Sum(F('quantity') * F('price')))['total'] or 0
        return f"₹{total_sales:.2f}"
    total_sales.short_description = "Total Sales"

    def popularity_score(self, obj):
        order_count = OrderItem.objects.filter(
            product__category=obj
        ).count()
        
        if order_count == 0:
            return "★☆☆☆☆"
        elif order_count <= 10:
            return "★★☆☆☆"
        elif order_count <= 25:
            return "★★★☆☆"
        elif order_count <= 50:
            return "★★★★☆"
        else:
            return "★★★★★"
    popularity_score.short_description = "Popularity"

    def stock_health(self, obj):
        """Show overall stock health for this category"""
        products = obj.products.all()
        if not products:
            return "No products"
        
        out_of_stock = products.filter(stock_quantity=0).count()
        low_stock = products.filter(stock_quantity__lte=5, stock_quantity__gt=0).count()
        healthy_stock = products.filter(stock_quantity__gt=5).count()
        
        if out_of_stock == products.count():
            return format_html('<span style="color: red; font-weight: bold;">🔴 All Out</span>')
        elif out_of_stock > 0:
            return format_html('<span style="color: orange; font-weight: bold;">🟡 {} Out</span>', out_of_stock)
        elif low_stock > 0:
            return format_html('<span style="color: blue; font-weight: bold;">🔵 {} Low</span>', low_stock)
        else:
            return format_html('<span style="color: green; font-weight: bold;">🟢 Healthy</span>')
    stock_health.short_description = "Stock Health"

# =====================================================
# 🪴 Product Admin with Automatic Stock Management
# =====================================================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock_quantity", "sold_quantity", "available_stock", 
                   "reserved_stock", "stock_status_display", "total_revenue", "sales_velocity", "is_featured")
    list_filter = ("category", "is_featured", "created_at")
    search_fields = ("name", "category__name")
    ordering = ["name"]
    list_per_page = 25
    readonly_fields = ("sold_quantity", "available_stock", "reserved_stock", "stock_status_display", 
                      "total_revenue", "sales_velocity", "stock_health", "stock_breakdown")
    actions = ["restock_products", "mark_as_featured", "mark_as_not_featured", 
               "generate_sales_report", "update_stock_levels", "clear_reserved_stock",
               "auto_adjust_stock"]
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "category", "description", "image")
        }),
        ("Pricing & Inventory", {
            "fields": ("price", "stock_quantity", "sold_quantity", "available_stock", "reserved_stock", 
                      "stock_status_display", "stock_health")
        }),
        ("Stock Breakdown", {
            "fields": ("stock_breakdown",)
        }),
        ("Sales Analytics", {
            "fields": ("total_revenue", "sales_velocity")
        }),
        ("Display", {
            "fields": ("is_featured",)
        }),
    )

    def available_stock(self, obj):
        """Calculate available stock: stock_quantity - sold_quantity"""
        return max(obj.stock_quantity - obj.sold_quantity, 0)
    available_stock.short_description = "Available Stock"

    def reserved_stock(self, obj):
        """Calculate reserved stock (in confirmed/processing/shipped orders)"""
        reserved = OrderItem.objects.filter(
            product=obj,
            order__status__in=['confirmed', 'processing', 'shipped']
        ).aggregate(total=Sum('quantity'))['total'] or 0
        return reserved
    reserved_stock.short_description = "Reserved Stock"

    def stock_status_display(self, obj):
        available = self.available_stock(obj)
        
        if available == 0:
            return format_html('<span style="color: red; font-weight: bold;">🔴 Out of Stock</span>')
        elif available <= 5:
            return format_html('<span style="color: orange; font-weight: bold;">🟡 Low Stock ({})</span>', available)
        elif available <= 15:
            return format_html('<span style="color: blue; font-weight: bold;">🔵 Medium Stock ({})</span>', available)
        else:
            return format_html('<span style="color: green; font-weight: bold;">🟢 In Stock ({})</span>', available)
    stock_status_display.short_description = "Stock Status"

    def stock_health(self, obj):
        """Show stock health indicator"""
        available = self.available_stock(obj)
        
        if available == 0:
            return format_html('<span style="color: red; font-weight: bold;">❌ CRITICAL - No Stock</span>')
        elif available <= 3:
            return format_html('<span style="color: orange; font-weight: bold;">⚠️ VERY LOW - {} available</span>', available)
        elif available <= 10:
            return format_html('<span style="color: #FFA500; font-weight: bold;">📉 LOW - {} available</span>', available)
        else:
            return format_html('<span style="color: green; font-weight: bold;">✅ HEALTHY - {} available</span>', available)
    stock_health.short_description = "Stock Health"

    def stock_breakdown(self, obj):
        """Show detailed stock breakdown"""
        total_stock = obj.stock_quantity
        sold = obj.sold_quantity
        reserved = self.reserved_stock(obj)
        available = self.available_stock(obj)
        
        breakdown = [
            f"📦 Total Stock: {total_stock} units",
            f"💰 Sold/Delivered: {sold} units",
            f"📋 Reserved (in process): {reserved} units",
            f"✅ Available for Sale: {available} units"
        ]
        
        # Calculate stock utilization
        if total_stock > 0:
            utilization = (sold / total_stock) * 100
            breakdown.append(f"📊 Stock Utilization: {utilization:.1f}%")
        
        # Show pending orders that will affect stock
        pending_orders = OrderItem.objects.filter(
            product=obj,
            order__status='pending'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        if pending_orders > 0:
            breakdown.append(f"⏳ Pending Orders: {pending_orders} units")
        
        return format_html("<br>".join(breakdown))
    stock_breakdown.short_description = "Stock Breakdown"

    def total_revenue(self, obj):
        revenue = obj.sold_quantity * obj.price
        return f"₹{revenue:.2f}"
    total_revenue.short_description = "Total Revenue"

    def sales_velocity(self, obj):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_sales = OrderItem.objects.filter(
            product=obj,
            order__created_at__gte=thirty_days_ago,
            order__status='delivered'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        velocity = recent_sales / 4.0
        
        if velocity == 0:
            return "📊 No recent sales"
        elif velocity < 5:
            return f"🐢 Slow ({velocity:.1f}/week)"
        elif velocity < 15:
            return f"🚶 Medium ({velocity:.1f}/week)"
        else:
            return f"🚀 Fast ({velocity:.1f}/week)"
    sales_velocity.short_description = "Sales Velocity"

    def restock_products(self, request, queryset):
        for product in queryset:
            product.stock_quantity += 50
            product.save()
        self.message_user(request, f"✅ Successfully restocked {queryset.count()} products (+50 units each).", messages.SUCCESS)
    restock_products.short_description = "🔄 Restock products (+50 units)"

    def update_stock_levels(self, request, queryset):
        """Update stock levels based on actual delivered orders"""
        updated_count = 0
        for product in queryset:
            # Calculate actual sold quantity from delivered orders
            actual_sold = OrderItem.objects.filter(
                product=product,
                order__status='delivered'
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            # Update the product's sold quantity
            if product.sold_quantity != actual_sold:
                product.sold_quantity = actual_sold
                product.save()
                updated_count += 1
        
        self.message_user(request, f"✅ Updated stock levels for {updated_count} products based on actual sales.", messages.SUCCESS)
    update_stock_levels.short_description = "📊 Sync stock with actual sales"

    def auto_adjust_stock(self, request, queryset):
        """Automatically adjust stock quantity based on sold items"""
        adjusted_count = 0
        for product in queryset:
            # If sold quantity exceeds stock quantity, adjust stock
            if product.sold_quantity > product.stock_quantity:
                old_stock = product.stock_quantity
                product.stock_quantity = product.sold_quantity
                product.save()
                adjusted_count += 1
                self.message_user(
                    request, 
                    f"🔄 {product.name}: Adjusted stock from {old_stock} to {product.sold_quantity}", 
                    messages.WARNING
                )
        
        if adjusted_count == 0:
            self.message_user(request, "✅ All products have sufficient stock levels.", messages.SUCCESS)
        else:
            self.message_user(request, f"✅ Auto-adjusted stock for {adjusted_count} products.", messages.SUCCESS)
    auto_adjust_stock.short_description = "🔄 Auto-adjust stock levels"

    def clear_reserved_stock(self, request, queryset):
        """Clear reserved stock by cancelling pending orders"""
        cleared_count = 0
        for product in queryset:
            pending_items = OrderItem.objects.filter(
                product=product,
                order__status='pending'
            )
            
            for item in pending_items:
                item.order.status = 'cancelled'
                item.order.save()
                cleared_count += 1
        
        self.message_user(request, f"✅ Cleared reserved stock by cancelling {cleared_count} pending order items.", messages.SUCCESS)
    clear_reserved_stock.short_description = "🗑️ Clear reserved stock"

    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"⭐ Marked {queryset.count()} products as featured.", messages.SUCCESS)
    mark_as_featured.short_description = "⭐ Mark as featured"

    def mark_as_not_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f"❌ Removed {queryset.count()} products from featured.", messages.SUCCESS)
    mark_as_not_featured.short_description = "❌ Remove from featured"

    def generate_sales_report(self, request, queryset):
        report_data = []
        total_revenue = 0
        total_sold = 0
        
        for product in queryset:
            revenue = product.sold_quantity * product.price
            total_revenue += revenue
            total_sold += product.sold_quantity
            available = self.available_stock(product)
            stock_status = "🟢" if available > 10 else "🟡" if available > 0 else "🔴"
            
            report_data.append(f"{stock_status} {product.name}: {product.sold_quantity} sold, ₹{revenue:.2f} revenue, {available} available")
        
        report = "\n".join(report_data)
        summary = f"\n\n📈 SUMMARY: {total_sold} total units sold, ₹{total_revenue:.2f} total revenue"
        
        self.message_user(request, f"📊 Sales Report:\n{report}{summary}", messages.INFO)
    generate_sales_report.short_description = "📊 Generate Sales Report"

# =====================================================
# 🛒 Order Admin with Automatic Stock Management
# =====================================================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "user", "status_display", "payment_method_display", "total_price", 
                   "items_count", "total_units", "stock_impact_status", "created_at", "order_age")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("user__username", "user__email", "id")
    ordering = ["-created_at"]
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    list_per_page = 20
    readonly_fields = ("created_at", "updated_at", "items_count", "total_units", "order_age", 
                      "order_value_analysis", "stock_impact_summary", "inventory_analysis")
    actions = [
        "mark_as_confirmed", 
        "mark_as_processing", 
        "mark_as_shipped", 
        "mark_as_delivered", 
        "mark_as_cancelled",
        "export_orders_analysis",
        "check_stock_availability",
        "auto_process_orders"
    ]
    
    fieldsets = (
        ("Order Information", {
            "fields": ("user", "address", "status", "payment_method", "total_price")
        }),
        ("Inventory Analysis", {
            "fields": ("inventory_analysis", "stock_impact_summary")
        }),
        ("Order Analytics", {
            "fields": ("items_count", "total_units", "order_age", "order_value_analysis")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )

    def order_id(self, obj):
        return f"ORDER#{obj.id:06d}"
    order_id.short_description = "Order ID"

    def status_display(self, obj):
        status_colors = {
            'pending': 'gray',
            'confirmed': 'blue', 
            'processing': 'orange',
            'shipped': 'purple',
            'delivered': 'green',
            'cancelled': 'red'
        }
        color = status_colors.get(obj.status, 'gray')
        status_text = dict(Order.STATUS_CHOICES).get(obj.status, obj.status)
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            color, status_text.upper()
        )
    status_display.short_description = "Status"

    def payment_method_display(self, obj):
        payment_text = dict(Order.PAYMENT_METHOD_CHOICES).get(obj.payment_method, obj.payment_method)
        return payment_text
    payment_method_display.short_description = "Payment Method"

    def items_count(self, obj):
        count = obj.items.count()
        return f"{count} items"
    items_count.short_description = "Items"

    def total_units(self, obj):
        total_items = obj.items.aggregate(total=Sum('quantity'))['total'] or 0
        return f"{total_items} units"
    total_units.short_description = "Total Units"

    def stock_impact_status(self, obj):
        if obj.status == 'cancelled':
            return format_html('<span style="color: gray;">🔄 Stock Restored</span>')
        elif obj.status == 'delivered':
            return format_html('<span style="color: green;">✅ Stock Updated</span>')
        else:
            issues = []
            for item in obj.items.all():
                available_stock = item.product.stock_quantity - item.product.sold_quantity
                if item.quantity > available_stock:
                    issues.append(f"{item.product.name}")
            
            if issues:
                return format_html('<span style="color: red; font-weight: bold;">⚠️ Low Stock: {}</span>', ", ".join(issues[:2]))
            else:
                return format_html('<span style="color: blue;">📦 Stock OK</span>')
    stock_impact_status.short_description = "Stock Impact"

    def inventory_analysis(self, obj):
        """Detailed inventory analysis for this order"""
        analysis = []
        total_impact = 0
        
        for item in obj.items.all():
            product = item.product
            current_stock = product.stock_quantity - product.sold_quantity
            after_stock = current_stock - item.quantity
            total_impact += item.quantity
            
            if after_stock < 0:
                analysis.append(
                    f"❌ {product.name}: {item.quantity} units → OVERSTOCK by {abs(after_stock)}"
                )
            elif after_stock == 0:
                analysis.append(
                    f"⚠️ {product.name}: {item.quantity} units → OUT OF STOCK after"
                )
            elif after_stock <= 3:
                analysis.append(
                    f"🟡 {product.name}: {item.quantity} units → {after_stock} left (VERY LOW)"
                )
            elif after_stock <= 10:
                analysis.append(
                    f"🔵 {product.name}: {item.quantity} units → {after_stock} left (LOW)"
                )
            else:
                analysis.append(
                    f"✅ {product.name}: {item.quantity} units → {after_stock} left (OK)"
                )
        
        if analysis:
            summary = f"<strong>📊 Total Impact: {total_impact} units across {len(analysis)} products</strong>"
            return format_html("{}<br>{}", summary, "<br>".join(analysis))
        return "No items in order"
    inventory_analysis.short_description = "Inventory Analysis"

    def stock_impact_summary(self, obj):
        summary = []
        for item in obj.items.all():
            current_stock = item.product.stock_quantity - item.product.sold_quantity
            after_stock = current_stock - item.quantity
            
            if after_stock < 0:
                summary.append(f"❌ {item.product.name}: OVERSTOCK by {abs(after_stock)}")
            elif after_stock == 0:
                summary.append(f"⚠️ {item.product.name}: Will be OUT OF STOCK")
            elif after_stock <= 3:
                summary.append(f"🟡 {item.product.name}: Very low ({after_stock} left)")
            elif after_stock <= 10:
                summary.append(f"🔵 {item.product.name}: Low ({after_stock} left)")
            else:
                summary.append(f"✅ {item.product.name}: OK ({after_stock} left)")
        
        return format_html("<br>".join(summary)) if summary else "No items in order"
    stock_impact_summary.short_description = "Stock Impact Details"

    def order_age(self, obj):
        age = timezone.now() - obj.created_at
        if age.days == 0:
            hours = age.seconds // 3600
            if hours == 0:
                minutes = (age.seconds // 60) % 60
                return f"{minutes} minutes ago"
            return f"{hours} hours ago"
        elif age.days == 1:
            return "1 day ago"
        else:
            return f"{age.days} days ago"
    order_age.short_description = "Order Age"

    def order_value_analysis(self, obj):
        if obj.total_price < 500:
            return format_html('<span style="color: orange;">📦 Small Order (₹{})</span>', obj.total_price)
        elif obj.total_price < 2000:
            return format_html('<span style="color: green;">📦 Medium Order (₹{})</span>', obj.total_price)
        else:
            return format_html('<span style="color: blue; font-weight: bold;">📦 Large Order (₹{})</span>', obj.total_price)
    order_value_analysis.short_description = "Order Value Analysis"

    def save_model(self, request, obj, form, change):
        old_status = None
        if obj.pk:
            try:
                old_obj = Order.objects.get(pk=obj.pk)
                old_status = old_obj.status
            except Order.DoesNotExist:
                pass

        super().save_model(request, obj, form, change)

        # ✅ Add success message properly
        if old_status != obj.status:
            messages.success(request, f"Order status changed from '{old_status}' to '{obj.status}'.")
            
            # Create status history when status changes
            OrderStatusHistory.objects.create(
                order=obj,
                status=obj.status,
                note=f"Status changed via admin by {request.user.username}"
            )
        else:
            messages.info(request, "Order updated successfully.")

        # Update total price
        if hasattr(obj, 'items') and obj.items.exists():
            total = sum(item.total_price for item in obj.items.all())
            if total != obj.total_price:
                obj.total_price = total
                Order.objects.filter(id=obj.id).update(total_price=total)

        # Handle stock updates based on status changes
        self.handle_stock_updates(obj, old_status)

    def handle_stock_updates(self, obj, old_status):
        """Handle automatic stock updates when order status changes"""
        if old_status != obj.status:
            # If order is cancelled and was previously confirmed/processing/shipped, restore stock
            if obj.status == 'cancelled' and old_status in ['confirmed', 'processing', 'shipped', 'delivered']:
                self.restore_stock(obj)
            
            # If order is delivered, finalize stock reduction
            elif obj.status == 'delivered' and old_status != 'delivered':
                self.finalize_stock_reduction(obj)
            
            # If order moves to confirmed/processing/shipped from pending, reserve stock
            elif obj.status in ['confirmed', 'processing', 'shipped'] and old_status == 'pending':
                self.reserve_stock(obj)

    def reserve_stock(self, obj):
        """Reserve stock when order is confirmed - increase sold_quantity"""
        for item in obj.items.all():
            product = item.product
            # Increase sold_quantity to reserve stock
            product.sold_quantity += item.quantity
            product.save()

    def finalize_stock_reduction(self, obj):
        """Finalize stock reduction when order is delivered - adjust stock_quantity"""
        for item in obj.items.all():
            product = item.product
            # Reduce actual stock quantity and maintain sold_quantity for records
            if product.stock_quantity >= item.quantity:
                product.stock_quantity -= item.quantity
                product.save()
            else:
                # If stock is insufficient, set to 0 and log the issue
                product.stock_quantity = 0
                product.save()

    def restore_stock(self, obj):
        """Restore stock when order is cancelled - decrease sold_quantity"""
        for item in obj.items.all():
            product = item.product
            # Decrease sold_quantity to restore available stock
            product.sold_quantity = max(0, product.sold_quantity - item.quantity)
            product.save()

    def save_formset(self, request, form, formset, change):
        """Save order items with stock validation"""
        instances = formset.save(commit=False)
        
        # Validate stock before saving
        stock_warnings = []
        for instance in instances:
            if instance.product:
                available_stock = instance.product.stock_quantity - instance.product.sold_quantity
                if instance.quantity > available_stock:
                    stock_warnings.append(
                        f"{instance.product.name}: Ordered {instance.quantity}, Available {available_stock}"
                    )
        
        # Show stock warnings
        if stock_warnings:
            self.message_user(
                request, 
                f"⚠️ Stock Warnings:\n" + "\n".join(stock_warnings), 
                messages.WARNING
            )
        
        for instance in instances:
            instance.save()
        formset.save_m2m()
        
        # Update order total after saving items
        if instances and hasattr(form.instance, 'items'):
            total = sum(item.total_price for item in form.instance.items.all())
            if total != form.instance.total_price:
                Order.objects.filter(id=form.instance.id).update(total_price=total)
                form.instance.total_price = total

    def check_stock_availability(self, request, queryset):
        """Check stock availability for selected orders"""
        for order in queryset:
            if order.status == 'pending':
                issues = []
                for item in order.items.all():
                    available_stock = item.product.stock_quantity - item.product.sold_quantity
                    if item.quantity > available_stock:
                        issues.append(f"{item.product.name}: Need {item.quantity}, Have {available_stock}")
                
                if issues:
                    self.message_user(
                        request, 
                        f"ORDER#{order.id}: ❌ Stock Issues:\n" + "\n".join(issues), 
                        messages.WARNING
                    )
                else:
                    self.message_user(
                        request, 
                        f"ORDER#{order.id}: ✅ Sufficient stock available", 
                        messages.SUCCESS
                    )
    check_stock_availability.short_description = "🔍 Check Stock Availability"

    def auto_process_orders(self, request, queryset):
        """Automatically process orders with sufficient stock"""
        processed_count = 0
        for order in queryset:
            if order.status == 'pending':
                # Check if all items have sufficient stock
                can_process = True
                for item in order.items.all():
                    available_stock = item.product.stock_quantity - item.product.sold_quantity
                    if item.quantity > available_stock:
                        can_process = False
                        break
                
                if can_process:
                    order.status = 'confirmed'
                    order.save()
                    self.reserve_stock(order)
                    processed_count += 1
                    self.message_user(
                        request,
                        f"✅ ORDER#{order.id}: Auto-processed to confirmed",
                        messages.SUCCESS
                    )
        
        self.message_user(request, f"✅ Auto-processed {processed_count} orders with sufficient stock.", messages.SUCCESS)
    auto_process_orders.short_description = "🤖 Auto-process orders with stock"

    def mark_as_confirmed(self, request, queryset):
        confirmed_count = 0
        for order in queryset:
            if order.status == 'pending':
                order.status = 'confirmed'
                order.save()
                self.reserve_stock(order)
                confirmed_count += 1
        
        self.message_user(request, f"✅ Marked {confirmed_count} orders as confirmed and reserved stock.", messages.SUCCESS)
    mark_as_confirmed.short_description = "✅ Confirm Orders & Reserve Stock"

    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f"🔄 Marked {updated} orders as processing.", messages.SUCCESS)
    mark_as_processing.short_description = "🔄 Mark as Processing"

    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f"🚚 Marked {updated} orders as shipped.", messages.SUCCESS)
    mark_as_shipped.short_description = "🚚 Mark as Shipped"

    def mark_as_delivered(self, request, queryset):
        delivered_count = 0
        for order in queryset:
            if order.status != 'delivered':
                order.status = 'delivered'
                order.save()
                self.finalize_stock_reduction(order)
                delivered_count += 1
        
        self.message_user(request, f"✅ Marked {delivered_count} orders as delivered and updated inventory.", messages.SUCCESS)
    mark_as_delivered.short_description = "✅ Deliver Orders & Update Stock"

    def mark_as_cancelled(self, request, queryset):
        cancelled_count = 0
        for order in queryset:
            if order.status != 'cancelled':
                self.restore_stock(order)
                order.status = 'cancelled'
                order.save()
                cancelled_count += 1
        
        self.message_user(request, f"❌ Cancelled {cancelled_count} orders and restored stock.", messages.SUCCESS)
    mark_as_cancelled.short_description = "❌ Cancel Orders & Restore Stock"

    def export_orders_analysis(self, request, queryset):
        total_orders = queryset.count()
        total_revenue = queryset.aggregate(total=Sum('total_price'))['total'] or 0
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        analysis = f"""
        📊 Orders Analysis Report:
        - Total Orders: {total_orders}
        - Total Revenue: ₹{total_revenue:.2f}
        - Average Order Value: ₹{avg_order_value:.2f}
        - Date Range: {queryset.earliest('created_at').created_at.date()} to {queryset.latest('created_at').created_at.date()}
        """
        
        self.message_user(request, analysis, messages.INFO)
    export_orders_analysis.short_description = "📊 Export Orders Analysis"

# =====================================================
# 🧾 Order Item Admin with Enhanced Analytics
# =====================================================
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price", "total_price_display", "stock_before", "stock_after", "revenue_contribution")
    search_fields = ("order__id", "product__name")
    list_filter = ("order__status", "order__created_at")
    ordering = ["-order__created_at"]
    list_per_page = 20
    readonly_fields = ("total_price_display", "stock_before", "stock_after", "revenue_contribution", "stock_impact_analysis")
    
    def total_price_display(self, obj):
        return f"₹{obj.total_price}" if obj.id else "N/A"
    total_price_display.short_description = "Total Price"

    def stock_before(self, obj):
        if obj.product:
            return obj.product.stock_quantity - obj.product.sold_quantity
        return 0
    stock_before.short_description = "Stock Before"

    def stock_after(self, obj):
        if obj.product:
            before = obj.product.stock_quantity - obj.product.sold_quantity
            after = before - obj.quantity
            return after
        return 0
    stock_after.short_description = "Stock After"

    def stock_impact_analysis(self, obj):
        if obj.product:
            before = obj.product.stock_quantity - obj.product.sold_quantity
            after = before - obj.quantity
            
            if after < 0:
                return format_html(
                    '<span style="color: red; font-weight: bold;">❌ NEGATIVE STOCK: {} → {}</span><br>'
                    '<small>Overstock by {} units</small>', 
                    before, after, abs(after)
                )
            elif after == 0:
                return format_html(
                    '<span style="color: orange; font-weight: bold;">⚠️ OUT OF STOCK AFTER</span><br>'
                    '<small>{} → {} units</small>', 
                    before, after
                )
            else:
                return format_html(
                    '<span style="color: green;">✅ Stock reduction: {} → {} units</span><br>'
                    '<small>{} units remaining</small>', 
                    before, after, after
                )
        return "N/A"
    stock_impact_analysis.short_description = "Stock Impact Analysis"

    def revenue_contribution(self, obj):
        if obj.order.status == 'delivered':
            order_total = obj.order.total_price
            item_total = obj.total_price
            percentage = (item_total / order_total) * 100 if order_total > 0 else 0
            return f"₹{item_total} ({percentage:.1f}%)"
        return "N/A"
    revenue_contribution.short_description = "Revenue Contribution"

# =====================================================
# 🔔 Notification Admin
# =====================================================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message_preview", "is_read", "created_at", "notification_age")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "message")
    ordering = ["-created_at"]
    list_per_page = 20
    actions = ["mark_as_read", "mark_as_unread"]
    
    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = "Message"

    def notification_age(self, obj):
        age = timezone.now() - obj.created_at
        if age.days == 0:
            hours = age.seconds // 3600
            if hours == 0:
                return "Just now"
            return f"{hours}h ago"
        elif age.days == 1:
            return "1 day ago"
        else:
            return f"{age.days} days ago"
    notification_age.short_description = "Age"

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"Marked {updated} notifications as read.", messages.SUCCESS)
    mark_as_read.short_description = "Mark as read"

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"Marked {updated} notifications as unread.", messages.SUCCESS)
    mark_as_unread.short_description = "Mark as unread"

# =====================================================
# 🏠 Address Admin
# =====================================================
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "city", "state", "postal_code", "is_default", "usage_count")
    search_fields = ("user__username", "full_name", "city", "state")
    list_filter = ("is_default", "state", "country")
    ordering = ["user"]
    list_per_page = 20

    def usage_count(self, obj):
        return obj.order_set.count()
    usage_count.short_description = "Times Used"

# =====================================================
# 🛍️ AddToCart Admin with Enhanced Analytics
# =====================================================
@admin.register(AddToCart)
class AddToCartAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "quantity", "total_price_display", "stock_available", "cart_age", "abandonment_risk")
    search_fields = ("user__username", "product__name")
    ordering = ["-added_at"]
    list_per_page = 20
    readonly_fields = ("added_at", "total_price_display", "stock_available", "cart_age", "abandonment_risk")
    
    def total_price_display(self, obj):
        return f"₹{obj.total_price}" if obj.id else "N/A"
    total_price_display.short_description = "Total Price"

    def stock_available(self, obj):
        if obj.product:
            return obj.product.stock_quantity - obj.product.sold_quantity
        return 0
    stock_available.short_description = "Stock Available"

    def cart_age(self, obj):
        age = timezone.now() - obj.added_at
        if age.days == 0:
            hours = age.seconds // 3600
            return f"{hours} hours"
        else:
            return f"{age.days} days"
    cart_age.short_description = "In Cart For"

    def abandonment_risk(self, obj):
        age = timezone.now() - obj.added_at
        if age.days > 7:
            return format_html('<span style="color: red; font-weight: bold;">🔴 High Risk</span>')
        elif age.days > 3:
            return format_html('<span style="color: orange;">🟡 Medium Risk</span>')
        else:
            return format_html('<span style="color: green;">🟢 Low Risk</span>')
    abandonment_risk.short_description = "Abandonment Risk"

# =====================================================
# 📞 Contact Admin
# =====================================================
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_resolved']
    list_filter = ['created_at', 'is_resolved']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_resolved']
    readonly_fields = ['created_at']

# =====================================================
# 📊 Order Status History Admin
# =====================================================
@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'created_at', 'note']
    list_filter = ['status', 'created_at']
    readonly_fields = ['order', 'status', 'created_at', 'note']
    search_fields = ['order__id', 'note']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

# =====================================================
# 🏠 Home Admin
# =====================================================
@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    list_display = ['title', 'subtitle', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'subtitle', 'content']

# =====================================================
# ⭐ Review Admin
# =====================================================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'product__name', 'comment']
    readonly_fields = ['created_at', 'updated_at']

# =====================================================
