from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta
import uuid

# =====================================================
# 👤 Custom User Model
# =====================================================
class User(AbstractUser):
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=15, blank=True, null=True)
    points = models.IntegerField(default=0)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    # Add this method to fix the admin error
    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff


# =====================================================
# 🌿 Plant Category Model
# =====================================================
class PlantCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Plant Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# =====================================================
# 🛒 Product Model - FIXED STOCK MANAGEMENT
# =====================================================
class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(PlantCategory, on_delete=models.CASCADE, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    sold_quantity = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def available_stock(self):
        """Returns the remaining stock available (read-only)."""
        return max(self.stock_quantity - self.sold_quantity, 0)

    def reduce_stock(self, quantity):
        """✅ FIXED: Reduce stock after a successful order."""
        if quantity > self.available_stock:
            raise ValueError(f"Not enough stock available. Available: {self.available_stock}, Requested: {quantity}")
        self.sold_quantity += quantity
        self.save(update_fields=["sold_quantity"])
        return True

    def increase_stock(self, quantity):
        """Increase stock (for admin use)."""
        self.stock_quantity += quantity
        self.save(update_fields=["stock_quantity"])
        return True


# =====================================================
# 🏡 Address Model (SINGLE DEFINITION - FIXED DUPLICATE)
# =====================================================
class Address(models.Model):
    ADDRESS_TYPES = [
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address_line = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50, default='India')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='home')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.state}"
    
    def save(self, *args, **kwargs):
        # If this is set as default and there are other default addresses, update them
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)


# =====================================================
# 📦 Order Model (with tracking)
# =====================================================
class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ("cod", "Cash on Delivery"),
        ("online", "Online Payment"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="cod")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    order_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    tracking_number = models.CharField(max_length=50, blank=True, null=True)
    estimated_delivery = models.DateField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} - {self.user.username}"

    def save(self, *args, **kwargs):
        # Generate order number if not set
        if not self.order_number:
            self.order_number = f"ORD{self.id:06d}" if self.id else "TEMP"
        super().save(*args, **kwargs)
        if self.order_number == "TEMP" and self.id:
            self.order_number = f"ORD{self.id:06d}"
            Order.objects.filter(id=self.id).update(order_number=self.order_number)

        # Auto-update total price from items
        if hasattr(self, 'items') and self.items.exists():
            total = sum(item.total_price for item in self.items.all())
            if total != self.total_price:
                Order.objects.filter(id=self.id).update(total_price=total)
                self.total_price = total

    @property
    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    @property 
    def get_payment_method_display(self):
        return dict(self.PAYMENT_METHOD_CHOICES).get(self.payment_method, self.payment_method)

    @property
    def customer_name(self):
        return self.address.full_name if self.address else self.user.username

    @property
    def customer_email(self):
        return self.user.email

    @property
    def customer_phone(self):
        return self.address.phone if self.address else self.user.contact or ""

    @property
    def shipping_address_full(self):
        if self.address:
            return f"{self.address.address_line}, {self.address.city}, {self.address.state} - {self.address.postal_code}, {self.address.country}"
        return "No address provided"

    @property
    def shipping_city(self):
        return self.address.city if self.address else ""

    @property
    def shipping_state(self):
        return self.address.state if self.address else ""

    @property
    def shipping_zipcode(self):
        return self.address.postal_code if self.address else ""

    @property
    def shipping_country(self):
        return self.address.country if self.address else "India"

    @property
    def total_amount(self):
        return self.total_price


# =====================================================
# 🧾 Order Item Model
# =====================================================
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    def save(self, *args, **kwargs):
        # Set price if not set
        if not self.price and self.product:
            self.price = self.product.price
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return round(self.quantity * self.price, 2)

    @property
    def product_name(self):
        return self.product.name


# =====================================================
# 🕐 Order Status History Model
# =====================================================
class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, related_name='status_history', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Order Status History"
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


# =====================================================
# 🛍️ Cart Model
# =====================================================
class AddToCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

    @property
    def total_price(self):
        return round(self.quantity * self.product.price, 2)


# =====================================================
# 🔔 Notification Model
# =====================================================
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification for {self.user.username}"


# =====================================================
# 🏠 Home Section
# =====================================================
class Home(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="home_banners/", blank=True, null=True)
    button_text = models.CharField(max_length=100, blank=True, null=True)
    button_link = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =====================================================
# 📞 Contact Model
# =====================================================
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} - {self.subject}"


# =====================================================
# ⭐ Review Model
# =====================================================
class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"