from django.urls import path, include
from django.contrib import admin

from django.conf import settings
from django.conf.urls.static import static
from services import views as service_views
from . import views

urlpatterns = [
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/providers/', views.admin_providers, name='admin_providers'),
    path('admin/services/', views.admin_services, name='admin_services'),
    path('admin/requests/', views.admin_requests, name='admin_requests'),
    path('admin/reports/', views.admin_reports, name='admin_reports'),
    path('admin/settings/', views.admin_settings, name='admin_settings'),
    path('admin/', admin.site.urls),

    # HOMEPAGE
    path('', views.home, name="home"),
    path('dashboard/', views.role_redirect, name="role_redirect"),
    path('client/dashboard/', views.client_dashboard, name="client_dashboard"),
    path('provider/dashboard/', service_views.provider_dashboard, name="provider_dashboard"),

    # APPS
    path('accounts/', include('accounts.urls')),
    path('requests/', include('requests.urls')),
    path('services/', include('services.urls')),
   path('payments/', include('payments.urls')),
   path('reviews/', include('reviews.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
