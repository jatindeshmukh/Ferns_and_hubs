# fronted/context_processors.py
from django.db import DatabaseError, OperationalError
from .models import AddToCart, Notification, User

def cart_count(request):
    """Add cart count to all templates"""
    cart_count = 0
    user_id = request.session.get('user_id')
    
    if user_id:
        try:
            # Use select_related or only() for better performance if needed
            user = User.objects.filter(id=user_id).first()
            if user:
                cart_count = AddToCart.objects.filter(user=user).count()
        except (DatabaseError, OperationalError):
            # Handle database connection issues
            pass
        except Exception as e:
            # Log other exceptions in development
            if hasattr(request, 'settings') and request.settings.DEBUG:
                print(f"Cart count error: {e}")
    
    return {'cart_items_count': cart_count}

def user_notifications(request):
    """Add user notifications to all templates"""
    notifications = []
    unread_notifications_count = 0
    user_id = request.session.get('user_id')
    
    if user_id:
        try:
            user = User.objects.filter(id=user_id).first()
            if user:
                # Optimize query by selecting only needed fields
                notifications = Notification.objects.filter(
                    user=user
                ).select_related('user').order_by('-created_at')[:5]
                
                unread_notifications_count = Notification.objects.filter(
                    user=user, 
                    is_read=False
                ).count()
        except (DatabaseError, OperationalError):
            # Handle database connection issues
            pass
        except Exception as e:
            # Log other exceptions in development
            if hasattr(request, 'settings') and request.settings.DEBUG:
                print(f"Notifications error: {e}")
    
    return {
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count
    }

def current_user(request):
    """Add current user to all templates"""
    user = None
    user_id = request.session.get('user_id')
    
    if user_id:
        try:
            # Get user with only necessary fields to optimize query
            user = User.objects.filter(id=user_id).only(
                'id', 'username', 'email', 'contact', 'points'
            ).first()
        except (DatabaseError, OperationalError):
            # Handle database connection issues
            pass
        except Exception as e:
            # Log other exceptions in development
            if hasattr(request, 'settings') and request.settings.DEBUG:
                print(f"Current user error: {e}")
    
    return {'user': user}

def site_settings(request):
    """Add site-wide settings to all templates"""
    return {
        'site_name': 'FernsHub',
        'site_description': 'Your one-stop shop for beautiful plants and gardening essentials',
        'support_email': 'support@fernshub.com',
        'support_phone': '+91-XXXXXXXXXX',
        'free_shipping_threshold': 500,
        'shipping_cost': 50,
    }

def order_context(request):
    """Add order-related context to templates"""
    user_id = request.session.get('user_id')
    pending_orders_count = 0
    
    if user_id:
        try:
            from .models import Order
            user = User.objects.filter(id=user_id).first()
            if user:
                pending_orders_count = Order.objects.filter(
                    user=user, 
                    status__in=['pending', 'confirmed', 'processing']
                ).count()
        except (DatabaseError, OperationalError):
            pass
    
    return {
        'pending_orders_count': pending_orders_count
    }