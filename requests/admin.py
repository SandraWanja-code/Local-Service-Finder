

# Register your models here.
from django.contrib import admin
from .models import ServiceRequest

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "service",
        "provider",
        "status",
        "payment_status",
        "payment_method",
        "amount_paid",
        "complaint_status",
        "requested_at",
    )
    list_filter = ("status", "payment_status", "payment_method", "complaint_status", "service")
    search_fields = ("user__username", "provider__user__username", "location", "mpesa_code", "complaint")
