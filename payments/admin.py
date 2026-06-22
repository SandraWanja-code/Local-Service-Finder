

# Register your models here.
from django.contrib import admin
from .models import PaymentRecord, TransactionLog


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):

    list_display = (
        "service_request",
        "recorded_by",
        "payment_method",
        "amount_paid",
        "mpesa_code",
        "recorded_at",
    )

    list_filter = (
        "payment_method",
        "recorded_at",
    )

    search_fields = (
        "service_request__user__username",
        "recorded_by__username",
        "mpesa_code",
    )


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):

    list_display = (
        "payment_record",
        "action",
        "performed_by",
        "created_at",
    )

    list_filter = (
        "action",
        "created_at",
    )

    search_fields = (
        "payment_record__mpesa_code",
        "performed_by__username",
    )