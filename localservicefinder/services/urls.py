from django.urls import path
from . import views

urlpatterns = [

path("become-provider/", views.become_provider, name="become_provider"),
path("edit-provider/", views.edit_provider, name="edit_provider"),

path("service/<int:service_id>/", views.providers_by_service, name="providers_by_service"),

path("provider/<int:provider_id>/", views.provider_profile, name="provider_profile"),
path("dashboard/", views.provider_dashboard, name="provider_dashboard"),
path("my-requests/", views.customer_requests, name="customer_requests"),

]