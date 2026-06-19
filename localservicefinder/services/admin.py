

# Register your models here.
from django.contrib import admin
from .models import Service, Provider

admin.site.register(Service)
admin.site.register(Provider)