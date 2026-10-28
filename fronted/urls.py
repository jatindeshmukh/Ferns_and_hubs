# fronted/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 🏠 HOME & STATIC PAGES
    path('', views.home, name='home'),
    path('shipping-returns/', views.shipping_returns, name='shipping_returns'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('blog/', views.blog, name='blog'),
    path('contact/', views.contact_view, name='contact'),
    path('about-us/', views.about_us, name='about_us'),

    # 🌿 PLANT CATEGORY PAGES
    path('categories/', views.all_categories, name='categories'),
    path('indoor-plants/', views.indoor_plants, name='indoor_plants'),
    path('outdoor-plants/', views.outdoor_plants, name='outdoor_plants'),
    path('medicinal-plants/', views.medicinal_plants, name='medicinal_plants'),
    path('flowering-plants/', views.flowering_plants, name='flowering_plants'),
    path('foliage-plants/', views.foliage_plants, name='foliage_plants'),
    path('ferns-palms/', views.ferns_palms, name='ferns_palms'),
    path('succulents-cactus/', views.succulents_cactus, name='succulents_cactus'),
    path('fruit-vegetable-plants/', views.fruit_vegetable_plants, name='fruit_vegetable_plants'),
    
    # ✅ Plant Accessories URL
    path('plant-accessories/', views.gardening_essentials, name='plant_accessories'),

    # 🛒 PRODUCT PAGES
    path('products/', views.all_products, name='all_products'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),

    # 🔎 SEARCH
    path('search/', views.product_search, name='product_search'),

    # 📂 COLLECTION / SHOP BY CATEGORY PAGES
    path('collections/gardening-essentials/', views.gardening_essentials, name='gardening_essentials'),
    path('collections/miniature-garden/', views.miniature_garden, name='miniature_garden'),
    path('collections/sustainable-gifting/', views.sustainable_gifting, name='sustainable_gifting'),
    path('collections/building-blocks/', views.building_blocks, name='building_blocks'),
    path('collections/sustainable-living/', views.sustainable_living, name='sustainable_living'),
    path('collections/plants/', views.plants_collection, name='plants_collection'),

    # 👤 USER AUTHENTICATION
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 🔐 PASSWORD RESET FLOW
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),

    # 🧭 USER DASHBOARD & PROFILE MANAGEMENT
    path('dashboard/', views.dashboard, name='dashboard'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('change-password/', views.change_password, name='change_password'),

    # ⚙️ ADMIN DASHBOARD
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # 🛍️ CART OPERATIONS
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),

    # 🧾 CHECKOUT & ORDER MANAGEMENT
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),

    # 🏡 ADDRESS MANAGEMENT
    path('add-address/', views.add_address, name='add_address'),
    path('manage-addresses/', views.manage_addresses, name='manage_addresses'),
    path('edit-address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('delete-address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('set-default-address/<int:address_id>/', views.set_default_address, name='set_default_address'),

    # 🔔 NOTIFICATIONS - COMPLETE SET
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('notifications/clear-all/', views.clear_all_notifications, name='clear_all_notifications'),
    path('notifications/unread-count/', views.get_unread_notifications_count, name='get_unread_notifications_count'),
    path('admin/send-notification/', views.send_notification, name='send_notification'),

    # 📁 CATEGORY VIEW
    path('category/<slug:category_slug>/', views.category_view, name='category_view'),

    # 🚀 BUY NOW FUNCTIONALITY
    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    
    # 📄 DOWNLOAD INVOICE PDF
    path('download-invoice/<int:order_id>/', views.download_invoice_pdf, name='download_invoice_pdf'),

    # 📝 REVIEWS
    path('products/<int:product_id>/review/', views.add_review, name='add_review'),
]