from django.urls import path
from . import views

urlpatterns = [

path("become-provider/", views.become_provider, name="become_provider"),
path("edit-provider/", views.edit_provider, name="edit_provider"),
]