from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from .forms import AddressForm
from django.contrib.auth.hashers import make_password, check_password
from decimal import Decimal
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from django.urls import reverse
from django.db.models import Sum, F
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from django.template.loader import render_to_string
import logging
import json

# Set up logger
logger = logging.getLogger(__name__)

from .models import (
    User, Product, PlantCategory, Order, OrderItem, Notification,
    AddToCart, Home, Address, Review
)

# ================================================================
# ✅ Utility Functions
# ================================================================
def get_logged_in_user(request):
    """Return logged-in user if exists, else None."""
    try:
        user_id = request.session.get('user_id')
        if user_id:
            return User.objects.filter(id=user_id).first()
        return None
    except Exception as e:
        logger.error(f"Error in get_logged_in_user: {str(e)}")
        return None

def get_cart_count(user):
    """Get cart items count for user"""
    try:
        if user and hasattr(user, 'id'):
            return AddToCart.objects.filter(user=user).count()
        return 0
    except Exception as e:
        logger.error(f"Error in get_cart_count: {str(e)}")
        return 0

def get_timeline_status(current_status):
    """Return timeline items with their completion status"""
    status_order = ['pending', 'confirmed', 'processing', 'shipped', 'delivered']
    timeline_items = []
    
    try:
        current_index = status_order.index(current_status) if current_status in status_order else 0
    except ValueError:
        current_index = 0
    
    for i, status in enumerate(status_order):
        if i < current_index:
            status_class = 'completed'
        elif i == current_index:
            status_class = 'active'
        else:
            status_class = 'upcoming'
            
        timeline_items.append({
            'status': status,
            'class': status_class,
            'display_name': status.replace('_', ' ').title()
        })
    
    return timeline_items

# ================================================================
# 🏠 HOME & STATIC PAGES (PUBLIC - NO LOGIN REQUIRED)
# ================================================================
def home(request):
    try:
        user = get_logged_in_user(request)
        categories = PlantCategory.objects.all()
        products = Product.objects.all()[:8]
        home_sections = Home.objects.filter(is_active=True).order_by('id')
        
        cart_items_count = get_cart_count(user)
        
        # Get notifications only if user is logged in
        notifications = []
        unread_notifications_count = 0
        if user:
            notifications = Notification.objects.filter(user=user).order_by('-created_at')[:5]
            unread_notifications_count = Notification.objects.filter(user=user, is_read=False).count()
        
        return render(request, 'home.html', {
            'user': user,
            'categories': categories,
            'products': products,
            'home_sections': home_sections,
            'cart_items_count': cart_items_count,
            'notifications': notifications,
            'unread_notifications_count': unread_notifications_count,
        })
    except Exception as e:
        logger.error(f"Error in home view: {str(e)}")
        messages.error(request, "Error loading home page.")
        return render(request, 'home.html')

def shipping_returns(request):
    user = get_logged_in_user(request)
    cart_items_count = get_cart_count(user)
    return render(request, 'home/shipping-returns.html', {
        'user': user,
        'cart_items_count': cart_items_count
    })

def privacy_policy(request):
    user = get_logged_in_user(request)
    cart_items_count = get_cart_count(user)
    return render(request, 'home/privacy_policy.html', {
        'user': user,
        'cart_items_count': cart_items_count
    })

def terms_conditions(request):
    user = get_logged_in_user(request)
    cart_items_count = get_cart_count(user)
    return render(request, 'home/terms_conditions.html', {
        'user': user,
        'cart_items_count': cart_items_count
    })

def blog(request):
    """Blog page - accessible to both logged in and non-logged in users"""
    user = get_logged_in_user(request)
    cart_items_count = get_cart_count(user)
    
    return render(request, 'blog.html', {
        'user': user,
        'cart_items_count': cart_items_count
    })

def contact_view(request):
    """Contact page - accessible to both logged in and non-logged in users"""
    user = get_logged_in_user(request)
    cart_items_count = get_cart_count(user)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Send email
        try:
            send_mail(
                f'Contact Form Submission from {name}',
                message,
                email,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully!')
        except Exception as e:
            logger.error(f"Error sending contact email: {str(e)}")
            messages.error(request, 'Error sending message. Please try again.')
        
        return redirect('contact')
    
    return render(request, 'contact.html', {
        'user': user,
        'cart_items_count': cart_items_count
    })

# ================================================================
# 🌿 CATEGORY & PRODUCT VIEWS (PUBLIC - NO LOGIN REQUIRED)
# ================================================================
def category_products(request, category_name, template_name):
    try:
        category = get_object_or_404(PlantCategory, name__iexact=category_name)
        products = Product.objects.filter(category=category)
        user = get_logged_in_user(request)
        cart_items_count = get_cart_count(user)
        
        return render(request, template_name, {
            'user': user,
            'category': category, 
            'products': products,
            'cart_items_count': cart_items_count
        })
    except Exception as e:
        logger.error(f"Error in category_products: {str(e)}")
        messages.error(request, "Error loading category.")
        return redirect('home')

# Category shortcuts
def indoor_plants(request): 
    return category_products(request, "Indoor Plants", 'categories/indoor_plants.html')

def outdoor_plants(request): 
    return category_products(request, "Outdoor Plants", 'categories/outdoor_plants.html')

def medicinal_plants(request): 
    return category_products(request, "Medicinal Plants", 'categories/medicinal_plants.html')

def flowering_plants(request): 
    return category_products(request, "Flowering Plants", 'categories/flowering_plants.html')

def foliage_plants(request): 
    return category_products(request, "Foliage Plants", 'categories/foliage_plants.html')

def ferns_palms(request):
    return category_products(request, "Ferns & Palms", 'categories/ferns_palms.html')

def succulents_cactus(request): 
    return category_products(request, "Succulents & Cactus", 'categories/succulents_cactus.html')

def fruit_vegetable_plants(request): 
    return category_products(request, "Fruit & Vegetable Plants", 'categories/fruit_vegetable_plants.html')

# Collection views
def gardening_essentials(request):
    return category_products(request, "Gardening Essentials", 'collections/gardening_essentials.html')

def miniature_garden(request):
    return category_products(request, "Miniature Garden", 'collections/miniature_garden.html')

def sustainable_gifting(request):
    return category_products(request, "Sustainable Gifting", 'collections/sustainable_gifting.html')

def building_blocks(request):
    return category_products(request, "Building Blocks", 'collections/building_blocks.html')

def sustainable_living(request):
    return category_products(request, "Sustainable Living", 'collections/sustainable_living.html')

def plants_collection(request):
    return category_products(request, "Plants Collection", 'collections/plants_collection.html')

# Product views
def all_products(request):
    try:
        products = Product.objects.all()
        user = get_logged_in_user(request)
        cart_items_count = get_cart_count(user)
        
        return render(request, 'all_products.html', {
            'user': user,
            'products': products,
            'cart_items_count': cart_items_count
        })
    except Exception as e:
        logger.error(f"Error in all_products: {str(e)}")
        messages.error(request, "Error loading products.")
        return redirect('home')

def product_detail(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
        
        user = get_logged_in_user(request)
        cart_items_count = get_cart_count(user)
        
        reviews = Review.objects.filter(product=product).order_by('-created_at')
        
        context = {
            'user': user,
            'product': product,
            'related_products': related_products,
            'cart_items_count': cart_items_count,
            'reviews': reviews
        }
        
        return render(request, 'product_detail.html', context)
        
    except Exception as e:
        logger.error(f"Error in product_detail view for product_id {product_id}: {str(e)}")
        messages.error(request, "Error loading product.")
        return redirect('all_products')

def product_search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.none()
    user = get_logged_in_user(request)
    cart_items_count = get_cart_count(user)
    
    return render(request, 'product_search_results.html', {
        'user': user,
        'products': products, 
        'search_query': query,
        'cart_items_count': cart_items_count
    })

def category_view(request, category_slug):
    try:
        category = get_object_or_404(PlantCategory, slug=category_slug)
        products = Product.objects.filter(category=category)
        user = get_logged_in_user(request)
        cart_items_count = get_cart_count(user)
        
        return render(request, 'category.html', {
            'user': user,
            'category': category,
            'products': products,
            'cart_items_count': cart_items_count
        })
    except Exception as e:
        logger.error(f"Error in category_view: {str(e)}")
        messages.error(request, "Error loading category.")
        return redirect('home')

# ================================================================
# 👤 USER AUTHENTICATION
# ================================================================
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if not all([username, email, password]):
            messages.error(request, 'All fields are required.')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('signup')

        try:
            user = User.objects.create(username=username, email=email, password=make_password(password))
            request.session['user_id'] = user.id
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('home')
        except Exception as e:
            logger.error(f"Error in signup: {str(e)}")
            messages.error(request, 'Error creating account. Please try again.')
            return redirect('signup')

    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Incorrect password.')
        except User.DoesNotExist:
            messages.error(request, 'No user found with that email.')
        except Exception as e:
            logger.error(f"Error in login: {str(e)}")
            messages.error(request, 'Error during login. Please try again.')

    return render(request, 'login.html')

def logout_view(request):
    try:
        request.session.flush()
        messages.info(request, 'Logged out successfully.')
    except Exception as e:
        logger.error(f"Error in logout: {str(e)}")
    return redirect('home')

# ================================================================
# 🔐 PASSWORD RESET
# ================================================================
PASSWORD_RESET_TOKENS = {}

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email=email)
            token = get_random_string(40)
            PASSWORD_RESET_TOKENS[token] = user.id
            reset_link = request.build_absolute_uri(reverse('reset_password', args=[token]))

            send_mail(
                'FernsHub Password Reset',
                f"Hello {user.username},\n\nClick below to reset your password:\n{reset_link}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'Password reset link sent to your email.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
        except Exception as e:
            logger.error(f"Error in forgot_password: {str(e)}")
            messages.error(request, 'Error sending reset email. Please try again.')

    return render(request, 'forgot_password.html')

def reset_password(request, token):
    user_id = PASSWORD_RESET_TOKENS.get(token)
    if not user_id:
        messages.error(request, 'Invalid or expired reset link.')
        return redirect('forgot_password')

    try:
        user = get_object_or_404(User, id=user_id)
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return redirect('reset_password', token=token)

            user.password = make_password(new_password)
            user.save()
            PASSWORD_RESET_TOKENS.pop(token, None)
            messages.success(request, 'Password changed successfully!')
            return redirect('login')

        return render(request, 'reset_password.html', {'token': token})
    except Exception as e:
        logger.error(f"Error in reset_password: {str(e)}")
        messages.error(request, 'Error resetting password.')
        return redirect('forgot_password')

# ================================================================
# 🧭 USER DASHBOARD & PROFILE (PROTECTED - LOGIN REQUIRED)
# ================================================================
def dashboard(request):
    user = get_logged_in_user(request)
    if not user:
        messages.error(request, 'Please log in first.')
        return redirect('login')

    try:
        # Get orders and notifications
        orders = Order.objects.filter(user=user).order_by('-created_at')
        notifications = Notification.objects.filter(user=user).order_by('-created_at')[:5]
        addresses = Address.objects.filter(user=user).order_by('-is_default', '-id')
        cart_items_count = get_cart_count(user)

        # Calculate dashboard statistics
        total_orders = orders.count()
        delivered_count = orders.filter(status='delivered').count()
        pending_count = orders.filter(status__in=['pending', 'confirmed', 'processing', 'shipped']).count()
        total_spent = sum(order.total_price for order in orders if order.total_price)

        # Get recent orders for dashboard
        recent_orders = orders[:5]

        # Calculate tab-specific counts
        address_count = addresses.count()
        unread_notifications = notifications.filter(is_read=False).count()

        context = {
            'user': user,
            'orders': recent_orders,  # Show only recent orders on dashboard
            'notifications': notifications,
            'addresses': addresses,  # Include addresses for display
            'cart_items_count': cart_items_count,
            
            # Statistics
            'total_orders': total_orders,
            'delivered_count': delivered_count,
            'pending_count': pending_count,
            'total_spent': total_spent,
            
            # Additional counts
            'address_count': address_count,
            'unread_notifications': unread_notifications,
            'all_orders_count': orders.count(),
            
            # Active tab (can be set via query parameter)
            'active_tab': request.GET.get('tab', 'overview')
        }

        return render(request, 'dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in dashboard: {str(e)}")
        messages.error(request, 'Error loading dashboard.')
        return render(request, 'dashboard.html', {
            'user': user,
            'active_tab': 'overview'
        })

def update_profile(request):
    user = get_logged_in_user(request)
    if not user:
        messages.error(request, 'Please log in first.')
        return redirect('login')

    if request.method == 'POST':
        try:
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard')
        except Exception as e:
            logger.error(f"Error in update_profile: {str(e)}")
            messages.error(request, 'Error updating profile.')

    return render(request, 'update_profile.html', {'user': user})

def change_password(request):
    user = get_logged_in_user(request)
    if not user:
        messages.error(request, 'Please log in first.')
        return redirect('login')

    if request.method == 'POST':
        current = request.POST.get('current_password')
        new = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')

        try:
            if not check_password(current, user.password):
                messages.error(request, 'Incorrect current password.')
                return redirect('change_password')

            if new != confirm:
                messages.error(request, 'Passwords do not match.')
                return redirect('change_password')

            user.password = make_password(new)
            user.save()
            messages.success(request, 'Password updated successfully!')
            return redirect('dashboard')
        except Exception as e:
            logger.error(f"Error in change_password: {str(e)}")
            messages.error(request, 'Error changing password.')

    return render(request, 'change_password.html', {'user': user})

# ================================================================
# ⚙️ ADMIN DASHBOARD (PROTECTED - STAFF REQUIRED)
# ================================================================
@staff_member_required
def admin_dashboard(request):
    try:
        total_users = User.objects.count()
        total_orders = Order.objects.count()
        total_products = Product.objects.count()
        total_sales = OrderItem.objects.aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0

        return render(request, 'admin_dashboard.html', {
            'total_users': total_users,
            'total_orders': total_orders,
            'total_products': total_products,
            'total_sales': total_sales
        })
    except Exception as e:
        logger.error(f"Error in admin_dashboard: {str(e)}")
        messages.error(request, 'Error loading admin dashboard.')
        return render(request, 'admin_dashboard.html')

# ================================================================
# 🛍️ CART OPERATIONS (PROTECTED) - CLEAN & FIXED
# ================================================================
from django.db import transaction
from decimal import Decimal

def view_cart(request):
    user = get_logged_in_user(request)
    if not user: 
        messages.error(request, 'Please log in to view your cart.')
        return redirect('login')
    
    try:
        cart_items = AddToCart.objects.filter(user=user).select_related('product')
        total = sum(item.total_price for item in cart_items)

        return render(request, 'view_cart.html', {
            'user': user,
            'cart_items': cart_items, 
            'total': total,
            'cart_items_count': cart_items.count()
        })

    except Exception as e:
        logger.error(f"Error in view_cart: {str(e)}")
        messages.error(request, 'Error loading cart.')
        return redirect('home')


@require_POST
def add_to_cart(request, product_id):
    user = get_logged_in_user(request)
    if not user:
        response_data = {
            'success': False,
            'error': 'Please log in first.',
            'redirect_url': f'/login/?next={request.path}'
        }
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(response_data)
        messages.error(request, response_data['error'])
        return redirect('login')

    try:
        product = Product.objects.get(id=product_id)
        quantity = int(request.POST.get('quantity', 1))

        # Validate quantity
        if quantity < 1:
            response_data = {
                'success': False,
                'error': 'Invalid quantity.'
            }
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)
            messages.error(request, response_data['error'])
            return redirect('product_detail', product_id=product_id)

        # Check stock availability
        if quantity > product.available_stock:
            response_data = {
                'success': False,
                'error': f'Only {product.available_stock} units available.'
            }
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)
            messages.error(request, response_data['error'])
            return redirect('product_detail', product_id=product_id)

        with transaction.atomic():
            item, created = AddToCart.objects.get_or_create(user=user, product=product)

            if created:
                item.quantity = quantity
            else:
                new_quantity = item.quantity + quantity
                if new_quantity > product.available_stock:
                    response_data = {
                        'success': False,
                        'error': f'Max available: {product.available_stock}'
                    }
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse(response_data)
                    messages.error(request, response_data['error'])
                    return redirect('view_cart')
                item.quantity = new_quantity
            item.save()

        # Update cart count for response
        cart_items_count = AddToCart.objects.filter(user=user).count()
        
        response_data = {
            'success': True,
            'message': f"{product.name} added to cart",
            'cart_items_count': cart_items_count
        }
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(response_data)
            
        messages.success(request, response_data['message'])
        return redirect('view_cart')

    except Exception as e:
        logger.error(f"Error adding to cart: {str(e)}", exc_info=True)
        response_data = {
            'success': False,
            'error': 'Error adding item to cart.'
        }
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(response_data)
        messages.error(request, response_data['error'])
        return redirect('home')


def remove_from_cart(request, item_id):
    user = get_logged_in_user(request)
    if not user:
        return JsonResponse({
            'success': False, 
            'error': 'Please log in first.',
            'redirect_url': '/login/'
        }, status=401)

    try:
        item = get_object_or_404(AddToCart, id=item_id, user=user)
        item.delete()
        
        cart_items = AddToCart.objects.filter(user=user)
        cart_total = sum(item.total_price for item in cart_items)
        
        return JsonResponse({
            'success': True,
            'message': "Item removed from cart",
            'total': cart_total,
            'cart_empty': not cart_items.exists(),
            'cart_items_count': cart_items.count()
        })

    except Exception as e:
        logger.error(f"Error removing item: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error removing item from cart'
        }, status=400)


@require_POST
def update_cart_quantity(request, item_id):
    user = get_logged_in_user(request)
    if not user:
        return JsonResponse({
            'success': False, 
            'error': 'Please log in first.',
            'redirect_url': '/login/'
        }, status=401)

    try:
        item = get_object_or_404(AddToCart, id=item_id, user=user)
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))

        if quantity < 1:
            return JsonResponse({
                'success': False,
                'error': 'Invalid quantity.'
            })

        if quantity > item.product.available_stock:
            return JsonResponse({
                'success': False,
                'error': f"Only {item.product.available_stock} units available."
            })

        item.quantity = quantity
        item.save()

        cart_items = AddToCart.objects.filter(user=user)
        cart_total = sum(i.total_price for i in cart_items)

        return JsonResponse({
            'success': True,
            'message': 'Cart updated successfully',
            'item_total': item.total_price,
            'total': cart_total,
            'cart_items_count': cart_items.count()
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid request format.'
        }, status=400)
    except Exception as e:
        logger.error(f"Error updating quantity: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error updating quantity.'
        }, status=400)

# 🛒 CHECKOUT & ORDER PROCESSING (PROTECTED)
# ================================================================
from decimal import Decimal
from django.db import transaction

def checkout(request):
    user = get_logged_in_user(request)
    if not user:
        messages.error(request, "Please log in to checkout.")
        return redirect('login')

    try:
        cart_items = AddToCart.objects.filter(user=user).select_related('product')

        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('view_cart')

        cart_total = Decimal(str(sum(item.total_price for item in cart_items)))
        tax_rate = Decimal('0.18')
        tax_amount = (cart_total * tax_rate).quantize(Decimal('0.01'))
        grand_total = (cart_total + tax_amount).quantize(Decimal('0.01'))

        addresses = Address.objects.filter(user=user).order_by('-is_default', '-id')

        context = {
            "user": user,
            "cart_items": cart_items,
            "cart_total": cart_total,
            "tax_amount": tax_amount,
            "grand_total": grand_total,
            "addresses": addresses,
            "cart_items_count": cart_items.count()
        }

        # ✅ GET request: show checkout page
        if request.method == 'GET':
            return render(request, "checkout.html", context)

        # ✅ POST request: placing order
        if request.method == 'POST':
            address_id = request.POST.get("address_id")
            payment_method = request.POST.get("payment_method", "cod")

            if not address_id:
                messages.error(request, "Please select a delivery address.")
                return redirect("checkout")

            address = get_object_or_404(Address, id=address_id, user=user)

            with transaction.atomic():
                order = Order.objects.create(
                    user=user,
                    address=address,
                    total_price=grand_total,
                    status="confirmed",
                    payment_method=payment_method
                )

                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )

                    product = item.product
                    product.reduce_stock(item.quantity)

                # Clear cart
                cart_items.delete()

                messages.success(request, f"Order #{order.id} placed successfully!")

                # Send order confirmation email to the user (best-effort)
                try:
                    if user.email:
                        email_context = {
                            'user': user,
                            'order': order,
                            'order_items': OrderItem.objects.filter(order=order).select_related('product'),
                            'order_date': order.created_at or timezone.now(),
                            'order_url': request.build_absolute_uri(reverse('order_detail', args=[order.id]))
                        }

                        subject = f"FernsHub Order Confirmation - #{order.id}"
                        plain_message = render_to_string('emails/order_confirmation_email.txt', email_context)
                        html_message = render_to_string('emails/order_confirmation_email.html', email_context)

                        send_mail(
                            subject,
                            plain_message,
                            settings.DEFAULT_FROM_EMAIL,
                            [user.email],
                            html_message=html_message,
                            fail_silently=True,
                        )
                except Exception as e:
                    logger.error(f"Error sending order confirmation email for order {order.id}: {str(e)}")

                # Prepare context for order confirmation page
                order_items = OrderItem.objects.filter(order=order).select_related('product')

                # Financials: subtotal, tax, shipping, final amount
                subtotal = sum((item.total_price for item in order_items)) if order_items else 0
                tax_rate_percent = getattr(settings, 'TAX_RATE', 5)  # percent (e.g., 5 means 5%)
                try:
                    tax_rate_decimal = Decimal(tax_rate_percent) / Decimal(100)
                except Exception:
                    tax_rate_decimal = Decimal('0.05')
                    tax_rate_percent = 5

                tax_amount = (Decimal(subtotal) * tax_rate_decimal).quantize(Decimal('0.01'))

                free_threshold = getattr(settings, 'FREE_SHIPPING_THRESHOLD', 0)
                shipping_cost_setting = getattr(settings, 'SHIPPING_COST', 0)
                shipping_fee = 0 if Decimal(subtotal) >= Decimal(free_threshold) else Decimal(shipping_cost_setting)

                final_amount = (Decimal(subtotal) + tax_amount + Decimal(shipping_fee)).quantize(Decimal('0.01'))

                # Get timeline status
                timeline_items = get_timeline_status(order.status)

                # Calculate estimated delivery
                if order.created_at:
                    estimated_delivery = order.created_at + timedelta(days=5)
                    order_date = order.created_at.strftime("%B %d, %Y")
                    estimated_delivery_str = estimated_delivery.strftime("%B %d, %Y")
                else:
                    order_date = timezone.now().strftime("%B %d, %Y")
                    estimated_delivery_str = (timezone.now() + timedelta(days=5)).strftime("%B %d, %Y")

                context = {
                    'user': user,
                    'order': order,
                    'order_items': order_items,
                    'timeline_items': timeline_items,
                    'cart_items_count': get_cart_count(user),
                    'title': f'Order Confirmation #{order.id}',
                    'order_date': order_date,
                    'estimated_delivery': estimated_delivery_str,
                    'subtotal': subtotal,
                    'shipping_fee': shipping_fee,
                    'tax_rate': tax_rate_percent,
                    'tax_amount': tax_amount,
                    'final_amount': final_amount,
                }

                return render(request, 'order_confirmation.html', context)

    except Exception as e:
        logger.error(f"Checkout Error: {e}")
        messages.error(request, f"There was an error: {e}")
        return redirect("view_cart")


# ================================================================
# ✅ ORDER CONFIRMATION VIEW (ENHANCED) (PROTECTED)
# ================================================================
def order_confirmation(request, order_id):
    """
    Display order confirmation page after successful checkout
    """
    user = get_logged_in_user(request)
    if not user:
        messages.error(request, 'Please log in to view your order.')
        return redirect('login')
    
    try:
        # Try to get the order for the current user
        try:
            order = Order.objects.get(id=order_id, user=user)
        except Order.DoesNotExist:
            # Fallback: if order exists but for some reason user lookup failed (session mismatch),
            # try to fetch the order by id and render it (log a warning).
            order = Order.objects.filter(id=order_id).first()
            if order:
                logger.warning(f"Order {order_id} found but not linked to current session user (user_id={getattr(user, 'id', None)}). Rendering fallback confirmation.")
                messages.info(request, "Showing order confirmation. If this isn't your order, contact support.")
            else:
                raise Order.DoesNotExist

        # Get order items
        order_items = order.orderitem_set.all()

        # Financials: subtotal, tax, shipping, final amount
        subtotal = sum((item.total_price for item in order_items)) if order_items else 0
        tax_rate_percent = getattr(settings, 'TAX_RATE', 5)  # percent (e.g., 5 means 5%)
        try:
            tax_rate_decimal = Decimal(tax_rate_percent) / Decimal(100)
        except Exception:
            tax_rate_decimal = Decimal('0.05')
            tax_rate_percent = 5

        tax_amount = (Decimal(subtotal) * tax_rate_decimal).quantize(Decimal('0.01'))

        free_threshold = getattr(settings, 'FREE_SHIPPING_THRESHOLD', 0)
        shipping_cost_setting = getattr(settings, 'SHIPPING_COST', 0)
        shipping_fee = 0 if Decimal(subtotal) >= Decimal(free_threshold) else Decimal(shipping_cost_setting)

        final_amount = (Decimal(subtotal) + tax_amount + Decimal(shipping_fee)).quantize(Decimal('0.01'))

        # Provide friendly aliases used by the template (some templates expect these attributes)
        order.email = getattr(order, 'customer_email', '')
        order.full_name = getattr(order, 'customer_name', '')
        order.city = getattr(order, 'shipping_city', '')
        order.state = getattr(order, 'shipping_state', '')
        order.postal_code = getattr(order, 'shipping_zipcode', '')
        order.country = getattr(order, 'shipping_country', 'India')
        order.phone = getattr(order, 'customer_phone', '')

        # Get timeline status
        timeline_items = get_timeline_status(order.status)

        # Calculate estimated delivery
        if order.created_at:
            estimated_delivery = order.created_at + timedelta(days=5)
            order_date = order.created_at.strftime("%B %d, %Y")
            estimated_delivery_str = estimated_delivery.strftime("%B %d, %Y")
        else:
            order_date = timezone.now().strftime("%B %d, %Y")
            estimated_delivery_str = (timezone.now() + timedelta(days=5)).strftime("%B %d, %Y")

        context = {
            'user': user,
            'order': order,
            'order_items': order_items,
            'timeline_items': timeline_items,
            'cart_items_count': get_cart_count(user),
            'title': f'Order Confirmation #{order.id}',
            'order_date': order_date,
            'estimated_delivery': estimated_delivery_str,
            'subtotal': subtotal,
            'shipping_fee': shipping_fee,
            'tax_rate': tax_rate_percent,
            'tax_amount': tax_amount,
            'final_amount': final_amount,
        }

        return render(request, 'order_confirmation.html', context)

    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('dashboard')
    except Exception as e:
        logger.error(f"Error loading order confirmation: {str(e)}")
        messages.error(request, 'Error loading order confirmation.')
        return redirect('dashboard')

# ================================================================
## 🏡 ADDRESS MANAGEMENT (PROTECTED)
# ================================================================
def manage_addresses(request):
    user = get_logged_in_user(request)
    if not user:
        messages.error(request, 'Please log in first.')
        return redirect('login')

    try:
        addresses = Address.objects.filter(user=user).order_by('-is_default', '-id')
        cart_items_count = get_cart_count(user)
        return render(request, 'manage_addresses.html', {
            'user': user,
            'addresses': addresses,
            'cart_items_count': cart_items_count
        })

    except Exception as e:
        logger.error(f"Error in manage_addresses: {str(e)}")
        messages.error(request, 'Error managing addresses.')
        return redirect('home')


def add_address(request):
    user = get_logged_in_user(request)
    if not user:
        messages.error(request, 'Please log in first.')
        return redirect('login')

    if request.method == 'POST':
        try:
            full_name = request.POST.get('full_name')
            phone = request.POST.get('phone')
            address_line = request.POST.get('address_line')
            city = request.POST.get('city')
            state = request.POST.get('state')
            postal_code = request.POST.get('postal_code')
            country = request.POST.get('country', 'India')
            is_default = request.POST.get('is_default') == 'on'

            # Validation
            form_errors = []
            if not all([full_name, phone, address_line, city, state, postal_code]):
                form_errors.append("Please fill in all required fields.")

            if phone and (len(phone) != 10 or not phone.isdigit()):
                form_errors.append("Enter valid 10-digit phone number.")

            if postal_code and (len(postal_code) != 6 or not postal_code.isdigit()):
                form_errors.append("Enter valid 6-digit postal code.")

            if form_errors:
                # Re-render the manage addresses page with form data and errors so the modal can show them
                addresses = Address.objects.filter(user=user).order_by('-is_default', '-id')
                cart_items_count = get_cart_count(user)
                form_data = {
                    'full_name': full_name,
                    'phone': phone,
                    'address_line': address_line,
                    'city': city,
                    'state': state,
                    'postal_code': postal_code,
                    'country': country,
                    'is_default': is_default,
                    'from_checkout': request.GET.get('from_checkout') or request.POST.get('from_checkout')
                }
                return render(request, 'manage_addresses.html', {
                    'user': user,
                    'addresses': addresses,
                    'cart_items_count': cart_items_count,
                    'form_errors': form_errors,
                    'form_data': form_data,
                })

            if is_default:
                Address.objects.filter(user=user, is_default=True).update(is_default=False)

            Address.objects.create(
                user=user,
                full_name=full_name,
                phone=phone,
                address_line=address_line,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country,
                is_default=is_default
            )

            messages.success(request, "Address added successfully!")

            # If user came from checkout (via GET) or the modal sent a POST flag, return to checkout
            if request.GET.get('from_checkout') or request.POST.get('from_checkout'):
                return redirect('checkout')

            return redirect('manage_addresses')

        except Exception as e:
            logger.error(f"Error in add_address: {str(e)}")
            messages.error(request, "Error adding address.")
            return redirect('manage_addresses')

    return redirect('manage_addresses')


def edit_address(request, address_id):
    user = get_logged_in_user(request)
    if not user:
        messages.error(request, 'Please log in first.')
        return redirect('login')

    try:
        address = get_object_or_404(Address, id=address_id, user=user)

        if request.method == 'POST':
            full_name = request.POST.get('full_name')
            phone = request.POST.get('phone')
            address_line = request.POST.get('address_line')
            city = request.POST.get('city')
            state = request.POST.get('state')
            postal_code = request.POST.get('postal_code')
            country = request.POST.get('country', 'India')
            is_default = request.POST.get('is_default') == 'on'

            if not all([full_name, phone, address_line, city, state, postal_code]):
                messages.error(request, "Please fill in all required fields.")
                return redirect('edit_address', address_id=address_id)

            if len(phone) != 10 or not phone.isdigit():
                messages.error(request, "Enter valid 10-digit phone number.")
                return redirect('edit_address', address_id=address_id)

            if len(postal_code) != 6 or not postal_code.isdigit():
                messages.error(request, "Enter valid 6-digit postal code.")
                return redirect('edit_address', address_id=address_id)

            if is_default and not address.is_default:
                Address.objects.filter(user=user, is_default=True).update(is_default=False)

            address.full_name = full_name
            address.phone = phone
            address.address_line = address_line
            address.city = city
            address.state = state
            address.postal_code = postal_code
            address.country = country
            address.is_default = is_default
            address.save()

            messages.success(request, "Address updated successfully!")

            # If user came from checkout (via GET) or the form included the hidden POST flag, return to checkout
            if request.GET.get('from_checkout') or request.POST.get('from_checkout'):
                return redirect('checkout')

            return redirect('manage_addresses')

        return render(request, 'edit_address.html', {
            'user': user,
            'address': address,
            'cart_items_count': get_cart_count(user)
        })

    except Exception as e:
        logger.error(f"Error in edit_address: {str(e)}")
        messages.error(request, "Error editing address.")
        return redirect('manage_addresses')


def delete_address(request, address_id):
    user = get_logged_in_user(request)
    if not user:
        messages.error(request, 'Please log in first.')
        return redirect('login')

    try:
        address = get_object_or_404(Address, id=address_id, user=user)

        if request.method == 'POST':
            address.delete()
            messages.success(request, "Address deleted successfully!")
            # Return to checkout if the action originated from there (GET or POST)
            if request.GET.get('from_checkout') or request.POST.get('from_checkout'):
                return redirect('checkout')
            return redirect('manage_addresses')

        return render(request, 'delete_address.html', {'user': user, 'address': address})

    except Exception as e:
        logger.error(f"Error in delete_address: {str(e)}")
        messages.error(request, "Error deleting address.")
        return redirect('manage_addresses')
    
    
    # ✅ Set Default Address
@require_POST
def set_default_address(request, address_id):
    user = get_logged_in_user(request)
    if not user:
        messages.error(request, "Please log in first.")
        return redirect('login')

    try:
        address = get_object_or_404(Address, id=address_id, user=user)

        # Remove previous default
        Address.objects.filter(user=user, is_default=True).update(is_default=False)

        # Set new one
        address.is_default = True
        address.save()

        messages.success(request, "Default address updated successfully!")
        return redirect('manage_addresses')

    except Exception as e:
        logger.error(f"Error in set_default_address: {str(e)}")
        messages.error(request, "Error setting default address.")
        return redirect('manage_addresses')



# ================================================================
# 📄 ADDITIONAL PAGES & FUNCTIONALITY
# ================================================================


def my_orders(request):
    """Display the user's order history or prompt for login"""
    user = get_logged_in_user(request)
    cart_items_count = get_cart_count(user)
    orders = []

    # If user is not logged in, show the template with login prompt
    if not user:
        return render(request, 'my_orders.html', {
            'user': None,
            'orders': [],
            'cart_items_count': 0,
            'show_login_prompt': True
        })
    
    # For logged in users, show their orders
    try:
        orders = Order.objects.filter(user=user).order_by('-created_at')
        return render(request, 'my_orders.html', {
            'user': user,
            'orders': orders,
            'cart_items_count': cart_items_count,
            'show_login_prompt': False
        })
    except Exception as e:
        logger.error(f"Error in my_orders: {str(e)}")
        messages.error(request, "Error loading orders.")
        return render(request, 'my_orders.html', {
            'user': user,
            'orders': [],
            'cart_items_count': cart_items_count,
            'show_login_prompt': False
        })

def about_us(request):
    """About Us page"""
    user = get_logged_in_user(request)
    cart_items_count = get_cart_count(user)
    
    return render(request, 'home/about_us.html', {
        'user': user,
        'cart_items_count': cart_items_count
    })

def all_categories(request):
    """Display all plant categories"""
    try:
        user = get_logged_in_user(request)
        categories = PlantCategory.objects.all()
        cart_items_count = get_cart_count(user)
        
        return render(request, 'categories/all_categories.html', {
            'user': user,
            'categories': categories,
            'cart_items_count': cart_items_count
        })
    except Exception as e:
        logger.error(f"Error in all_categories view: {str(e)}")
        return redirect('home')

def plant_accessories(request):
    """Plant Accessories page"""
    try:
        user = get_logged_in_user(request)
        cart_items_count = get_cart_count(user)
        
        # Get plant accessories products
        products = Product.objects.filter(category__name__icontains='accessory') | Product.objects.filter(category__name__icontains='gardening')
        
        return render(request, 'plant_accessories.html', {
            'user': user,
            'products': products,
            'cart_items_count': cart_items_count
        })
    except Exception as e:
        logger.error(f"Error in plant_accessories: {str(e)}")
        return redirect('all_products')

def ferns_palms(request):
    """Ferns & Palms category page"""
    try:
        user = get_logged_in_user(request)
        cart_items_count = get_cart_count(user)
        
        # Get products in Ferns & Palms category
        products = Product.objects.filter(category__name__icontains='fern') | Product.objects.filter(category__name__icontains='palm')
        
        return render(request, 'categories/ferns_palms.html', {
            'user': user,
            'products': products,
            'cart_items_count': cart_items_count,
            'category_name': 'Ferns & Palms'
        })
    except Exception as e:
        logger.error(f"Error in ferns_palms: {str(e)}")
        return redirect('categories')

def foliage_plants(request):
    """Foliage Plants category page"""
    try:
        user = get_logged_in_user(request)
        cart_items_count = get_cart_count(user)
        
        products = Product.objects.filter(category__name__icontains='foliage')
        
        return render(request, 'categories/foliage_plants.html', {
            'user': user,
            'products': products,
            'cart_items_count': cart_items_count,
            'category_name': 'Foliage Plants'
        })
    except Exception as e:
        logger.error(f"Error in foliage_plants: {str(e)}")
        return redirect('categories')

def succulents_cactus(request):
    """Succulents & Cactus category page"""
    try:
        user = get_logged_in_user(request)
        cart_items_count = get_cart_count(user)
        
        products = Product.objects.filter(category__name__icontains='succulent') | Product.objects.filter(category__name__icontains='cactus')
        
        return render(request, 'categories/succulents_cactus.html', {
            'user': user,
            'products': products,
            'cart_items_count': cart_items_count,
            'category_name': 'Succulents & Cactus'
        })
    except Exception as e:
        logger.error(f"Error in succulents_cactus: {str(e)}")
        return redirect('categories')

def fruit_vegetable_plants(request):
    """Fruit & Vegetable Plants category page"""
    try:
        user = get_logged_in_user(request)
        cart_items_count = get_cart_count(user)
        
        products = Product.objects.filter(category__name__icontains='fruit') | Product.objects.filter(category__name__icontains='vegetable')
        
        return render(request, 'categories/fruit_vegetable_plants.html', {
            'user': user,
            'products': products,
            'cart_items_count': cart_items_count,
            'category_name': 'Fruit & Vegetable Plants'
        })
    except Exception as e:
        logger.error(f"Error in fruit_vegetable_plants: {str(e)}")
        return redirect('categories')

def gardening_essentials(request):
    """Gardening Essentials category page"""
    try:
        user = get_logged_in_user(request)
        cart_items_count = get_cart_count(user)
        
        products = Product.objects.filter(category__name__icontains='gardening') | Product.objects.filter(category__name__icontains='tool')
        
        return render(request, 'categories/gardening_essentials.html', {
            'user': user,
            'products': products,
            'cart_items_count': cart_items_count,
            'category_name': 'Gardening Essentials'
        })
    except Exception as e:
        logger.error(f"Error in gardening_essentials: {str(e)}")
        return redirect('categories')

def indoor_plants(request):
    """Indoor Plants category page"""
    try:
        user = get_logged_in_user(request)
        cart_items_count = get_cart_count(user)
        
        products = Product.objects.filter(category__name__icontains='indoor')
        
        return render(request, 'categories/indoor_plants.html', {
            'user': user,
            'products': products,
            'cart_items_count': cart_items_count,
            'category_name': 'Indoor Plants'
        })
    except Exception as e:
        logger.error(f"Error in indoor_plants: {str(e)}")
        return redirect('categories')

def outdoor_plants(request):
    """Outdoor Plants category page"""
    try:
        user = get_logged_in_user(request)
        cart_items_count = get_cart_count(user)
        
        products = Product.objects.filter(category__name__icontains='outdoor')
        
        return render(request, 'categories/outdoor_plants.html', {
            'user': user,
            'products': products,
            'cart_items_count': cart_items_count,
            'category_name': 'Outdoor Plants'
        })
    except Exception as e:
        logger.error(f"Error in outdoor_plants: {str(e)}")
        return redirect('categories')

def flowering_plants(request):
    """Flowering Plants category page"""
    try:
        user = get_logged_in_user(request)
        cart_items_count = get_cart_count(user)
        
        products = Product.objects.filter(category__name__icontains='flowering')
        
        return render(request, 'categories/flowering_plants.html', {
            'user': user,
            'products': products,
            'cart_items_count': cart_items_count,
            'category_name': 'Flowering Plants'
        })
    except Exception as e:
        logger.error(f"Error in flowering_plants: {str(e)}")
        return redirect('categories')

def medicinal_plants(request):
    """Medicinal Plants category page"""
    try:
        user = get_logged_in_user(request)
        cart_items_count = get_cart_count(user)
        
        products = Product.objects.filter(category__name__icontains='medicinal')
        
        return render(request, 'categories/medicinal_plants.html', {
            'user': user,
            'products': products,
            'cart_items_count': cart_items_count,
            'category_name': 'Medicinal Plants'
        })
    except Exception as e:
        logger.error(f"Error in medicinal_plants: {str(e)}")
        return redirect('categories')

# ================================================================
# 🛒 MISSING VIEWS - ADDED TO FIX ERRORS
# ================================================================

from django.contrib.auth.decorators import login_required

def my_orders(request):
    """Display the user's order history or prompt for login"""
    user = get_logged_in_user(request)
    cart_items_count = get_cart_count(user)
    
    # Basic context for both logged in and non-logged in users
    context = {
        'user': user,
        'cart_items_count': cart_items_count,
        'orders': [],
        'show_login_prompt': not user
    }
    
    if user:
        try:
            orders = Order.objects.filter(user=user).order_by('-created_at')
            context['orders'] = orders
        except Exception as e:
            logger.error(f"Error in my_orders: {str(e)}")
            messages.error(request, "Error loading your orders.")
    
    return render(request, 'my_orders.html', context)

def order_detail(request, order_id):
    """Display details of a specific order"""
    
    # Check if user is logged in
    user = get_logged_in_user(request)
    if not user:
        # Store the target URL for post-login redirect
        next_url = request.get_full_path()
        messages.info(request, "Please log in to view order details")
        return redirect(f'/login/?next={next_url}')
    
    try:
        # Get the order and verify ownership
        order = get_object_or_404(Order, id=order_id)
        
        # Verify the order belongs to the user
        if order.user.id != user.id:
            messages.error(request, "You don't have permission to view this order.")
            return redirect('my_orders')
        
        # Prepare the status timeline
        status_timeline = [
            {
                'status': 'pending',
                'label': 'Order Placed',
                'description': 'Order is being reviewed'
            },
            {
                'status': 'confirmed',
                'label': 'Order Confirmed',  
                'description': 'Order has been confirmed'
            },
            {
                'status': 'processing',
                'label': 'Processing',
                'description': 'Order is being prepared'
            },
            {
                'status': 'shipped',
                'label': 'Shipped',
                'description': 'Order is on its way'
            },
            {
                'status': 'delivered',
                'label': 'Delivered',
                'description': 'Order has been delivered'
            }
        ]
        
        # Get the current status index
        current_status_index = next((i for i, s in enumerate(status_timeline) if s['status'] == order.status), 0)
            
        # Calculate relevant dates
        order_date = order.created_at.strftime("%B %d, %Y") if order.created_at else timezone.now().strftime("%B %d, %Y")
        estimated_delivery = (order.created_at if order.created_at else timezone.now()) + timedelta(days=5)
        estimated_delivery_str = estimated_delivery.strftime("%B %d, %Y")
        
        # Prepare context with all required data
        context = {
            'user': user,
            'order': order,
            'order_items': OrderItem.objects.filter(order=order).select_related('product'),
            'cart_items_count': get_cart_count(user),
            'status_timeline': status_timeline,
            'current_status_index': current_status_index,
            'order_date': order_date,
            'estimated_delivery': estimated_delivery_str
        }
        
        return render(request, 'order_detail.html', context)
        
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('my_orders')
    except Exception as e:
        logger.error(f"Error in order_detail view for order {order_id}: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while loading the order details. Please try again.")
        return redirect('my_orders')

# ================================================================
# 🔔 NOTIFICATION VIEWS (UPDATED & FIXED)
# ================================================================

def notifications(request):
    """Display user notifications page"""
    user = get_logged_in_user(request)
    if not user:
        messages.error(request, 'Please log in to view notifications.')
        return redirect('login')
    
    try:
        # Get all notifications for the user
        user_notifications = Notification.objects.filter(user=user).order_by('-created_at')
        cart_items_count = get_cart_count(user)
        
        # Count unread notifications
        unread_count = user_notifications.filter(is_read=False).count()
        
        context = {
            'user': user,
            'notifications': user_notifications,
            'cart_items_count': cart_items_count,
            'unread_count': unread_count,
            'title': 'My Notifications'
        }
        
        return render(request, 'notifications.html', context)
        
    except Exception as e:
        logger.error(f"Error in notifications view: {str(e)}")
        messages.error(request, "Error loading notifications.")
        return redirect('dashboard')


def mark_notification_read(request, notification_id):
    """Mark a specific notification as read"""
    user = get_logged_in_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'Please log in first.'})
    
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=user)
        notification.is_read = True
        notification.save()
        
        # Return success response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': 'Notification marked as read.',
                'unread_count': Notification.objects.filter(user=user, is_read=False).count()
            })
        
        messages.success(request, "Notification marked as read.")
        return redirect('notifications')
        
    except Exception as e:
        logger.error(f"Error in mark_notification_read: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Error marking notification as read.'})
        messages.error(request, "Error marking notification as read.")
        return redirect('notifications')


@require_POST
def mark_all_notifications_as_read(request):
    """Mark all user notifications as read"""
    user = get_logged_in_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'Please log in first.'})
    
    try:
        updated_count = Notification.objects.filter(user=user, is_read=False).update(is_read=True)
        
        # Return success response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': f'All {updated_count} notifications marked as read.',
                'unread_count': 0
            })
        
        messages.success(request, f"All {updated_count} notifications marked as read.")
        return redirect('notifications')
        
    except Exception as e:
        logger.error(f"Error in mark_all_notifications_as_read: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Error marking notifications as read.'})
        messages.error(request, "Error marking notifications as read.")
        return redirect('notifications')


def delete_notification(request, notification_id):
    """Delete a specific notification"""
    user = get_logged_in_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'Please log in first.'})
    
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=user)
        notification.delete()
        
        # Return success response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': 'Notification deleted.',
                'unread_count': Notification.objects.filter(user=user, is_read=False).count()
            })
        
        messages.success(request, "Notification deleted.")
        return redirect('notifications')
        
    except Exception as e:
        logger.error(f"Error in delete_notification: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Error deleting notification.'})
        messages.error(request, "Error deleting notification.")
        return redirect('notifications')


@require_POST
def clear_all_notifications(request):
    """Clear all notifications for the user"""
    user = get_logged_in_user(request)
    if not user:
        return JsonResponse({'success': False, 'error': 'Please log in first.'})
    
    try:
        deleted_count, _ = Notification.objects.filter(user=user).delete()
        
        # Return success response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': f'All {deleted_count} notifications cleared.',
                'unread_count': 0
            })
        
        messages.success(request, f"All {deleted_count} notifications cleared.")
        return redirect('notifications')
        
    except Exception as e:
        logger.error(f"Error in clear_all_notifications: {str(e)}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Error clearing notifications.'})
        messages.error(request, "Error clearing notifications.")
        return redirect('notifications')


def get_unread_notifications_count(request):
    """API endpoint to get unread notifications count (for AJAX requests)"""
    user = get_logged_in_user(request)
    if not user:
        return JsonResponse({'unread_count': 0})
    
    try:
        unread_count = Notification.objects.filter(user=user, is_read=False).count()
        return JsonResponse({'unread_count': unread_count})
    except Exception as e:
        logger.error(f"Error in get_unread_notifications_count: {str(e)}")
        return JsonResponse({'unread_count': 0})


@staff_member_required
def send_notification(request):
    """Send a notification to users (admin function)"""
    try:
        if request.method == 'POST':
            message = request.POST.get('message', '').strip()
            notification_type = request.POST.get('notification_type', 'info')
            
            if not message:
                messages.error(request, "Please enter a message.")
                return redirect('send_notification')
            
            users = User.objects.all()
            notification_count = 0
            
            for user in users:
                Notification.objects.create(
                    user=user,
                    message=message,
                    notification_type=notification_type
                )
                notification_count += 1
            
            messages.success(request, f"Notification sent to {notification_count} users.")
            return redirect('notifications')
        
        return render(request, 'admin/send_notification.html')
        
    except Exception as e:
        logger.error(f"Error in send_notification: {str(e)}")
        messages.error(request, "Error sending notification.")
        return redirect('dashboard')

# ================================================================
# 🚀 BUY NOW FUNCTIONALITY (MISSING VIEW)
# ================================================================

def buy_now(request, product_id):
    """Handle buy now functionality - direct purchase without adding to cart"""
    user = get_logged_in_user(request)
    if not user:
        messages.error(request, 'Please log in to purchase.')
        return redirect('login')
    
    try:
        product = get_object_or_404(Product, id=product_id)
        
        # Check stock availability
        if product.available_stock <= 0:
            messages.error(request, 'Product is out of stock.')
            return redirect('product_detail', product_id=product_id)
        
        # Clear existing cart items for this product
        AddToCart.objects.filter(user=user, product=product).delete()
        
        # Add product directly to cart with quantity 1
        AddToCart.objects.create(
            user=user,
            product=product,
            quantity=1
        )
        
        messages.success(request, f'Ready to purchase {product.name}!')
        return redirect('checkout')
        
    except Exception as e:
        logger.error(f"Error in buy_now for product {product_id}: {str(e)}")
        messages.error(request, 'Error processing buy now request.')
        return redirect('product_detail', product_id=product_id)

# ================================================================
# 📄 DOWNLOAD INVOICE PDF (MISSING VIEW)
# ================================================================

def download_invoice_pdf(request, order_id):
    """Generate and download invoice PDF"""
    user = get_logged_in_user(request)
    if not user:
        messages.error(request, 'Please log in to download invoice.')
        return redirect('login')
    
    try:
        order = get_object_or_404(Order, id=order_id, user=user)
        
        # For now, return a simple response - you can implement PDF generation later
        response = HttpResponse(f"Invoice for Order #{order_id}", content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="invoice_order_{order_id}.txt"'
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating invoice for order {order_id}: {str(e)}")
        messages.error(request, 'Error generating invoice.')
        return redirect('order_detail', order_id=order_id)

# ================================================================
# 📝 ADD REVIEW (MISSING VIEW)
# ================================================================

def add_review(request, product_id):
    """Add a review for a product"""
    user = get_logged_in_user(request)
    if not user:
        messages.error(request, 'Please log in to add a review.')
        return redirect('login')
    
    try:
        product = get_object_or_404(Product, id=product_id)
        
        if request.method == 'POST':
            rating = request.POST.get('rating')
            comment = request.POST.get('comment', '').strip()
            
            if not rating:
                messages.error(request, 'Please select a rating.')
                return redirect('product_detail', product_id=product_id)
            
            # Check if user already reviewed this product
            existing_review = Review.objects.filter(user=user, product=product).first()
            
            if existing_review:
                # Update existing review
                existing_review.rating = int(rating)
                existing_review.comment = comment
                existing_review.save()
                messages.success(request, 'Review updated successfully!')
            else:
                # Create new review
                Review.objects.create(
                    user=user,
                    product=product,
                    rating=int(rating),
                    comment=comment
                )
                messages.success(request, 'Review added successfully!')
            
            return redirect('product_detail', product_id=product_id)
        
        # GET request - redirect to product detail
        return redirect('product_detail', product_id=product_id)
        
    except Exception as e:
        logger.error(f"Error adding review for product {product_id}: {str(e)}")
        messages.error(request, 'Error adding review.')
        return redirect('product_detail', product_id=product_id)
    