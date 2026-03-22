
from django.urls import path
from . import views

urlpatterns = [
    
    path("request/", views.request_service, name="request_service"),
     path("my_requests/", views.customer_requests, name="customer_requests"),
    path("delete/<int:request_id>/", views.delete_request, name="delete_request"),
]