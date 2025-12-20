"""
URL configuration for leaders_academy project.
Main project URLs.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# JWT Authentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Template views
from lms.views import home, user_login, user_register, dashboard, user_logout

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # API Routes (all API endpoints under /api/)
    path('api/', include('lms.urls')),
    
    # JWT Authentication endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Template-based views (frontend pages)
    path('', home, name='home'),
    path('login/', user_login, name='login'),
    path('register/', user_register, name='register'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', user_logout, name='logout'),
]

# Serve static and media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)