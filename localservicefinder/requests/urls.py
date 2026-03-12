from django.urls import path
from . import views

urlpatterns = [
    path("request/", views.request_service, name="request_service"),
]