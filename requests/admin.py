

# Register your models here.
from django.contrib import admin
from .models import PaymentRecord, ProviderSelection, SearchHistory, ServiceRequest, TransactionLog

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


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "service", "location", "results_count", "searched_at")
    list_filter = ("searched_at", "service")
    search_fields = ("user__username", "location")


@admin.register(ProviderSelection)
class ProviderSelectionAdmin(admin.ModelAdmin):
    list_display = ("user", "provider", "service", "selected_at")
    list_filter = ("selected_at", "service")
    search_fields = ("user__username", "provider__user__username")


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ("service_request", "recorded_by", "payment_method", "amount_paid", "mpesa_code", "recorded_at")
    list_filter = ("payment_method", "recorded_at")
    search_fields = ("service_request__user__username", "recorded_by__username", "mpesa_code")


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ("payment_record", "action", "performed_by", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("payment_record__mpesa_code", "performed_by__username")
