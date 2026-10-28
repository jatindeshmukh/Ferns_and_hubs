
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin Panel
    path('admin/', admin.site.urls),

    # Include all routes from the 'fronted' app (home, login, signup, dashboard, etc.)
    path('', include('fronted.urls')),
]

# -------------------------------
# Development Mode: Serve Static & Media Files
# -------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
