

# Register your models here.
from django.contrib import admin
from .models import Service, Provider

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name", "description")
    list_filter = ("is_active",)


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "location", "approval_status", "is_available", "hourly_rate")
    list_filter = ("approval_status", "is_available", "services")
    search_fields = ("user__username", "user__email", "phone", "location", "credentials")
    filter_horizontal = ("services",)
