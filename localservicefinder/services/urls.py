from django.urls import path
from . import views

urlpatterns = [

    # PROVIDER FLOW
    path("become-provider/", views.become_provider, name="become_provider"),
    path("my-services/", views.my_services, name="my_services"),

    # EXISTING FEATURES
    path("service/<int:service_id>/", views.providers_by_service, name="providers_by_service"),
    path("provider/<int:provider_id>/", views.provider_profile, name="provider_profile"),
    path("dashboard/", views.provider_dashboard, name="provider_dashboard"),
    path("my-request/", views.customer_requests, name="customer_requests"),
    path('delete-account/', views.delete_account, name='delete_account'),
]