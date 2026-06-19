

# Register your models here.
from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Avg, Sum
from requests.models import ServiceRequest
from .models import ApprovalRecord, Provider, Service, ServiceCatalogueLog, SystemReport

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name", "description")
    list_filter = ("is_active",)

    def save_model(self, request, obj, form, change):
        action = "updated" if change else "created"
        super().save_model(request, obj, form, change)
        ServiceCatalogueLog.objects.create(
            service=obj,
            action=action,
            performed_by=request.user,
            details=f"Service category {action} from admin.",
        )


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "location", "approval_status", "is_available", "hourly_rate")
    list_filter = ("approval_status", "is_available", "services")
    search_fields = ("user__username", "user__email", "phone", "location", "credentials")
    filter_horizontal = ("services",)

    def save_model(self, request, obj, form, change):
        old_status = None
        if change and obj.pk:
            old_status = Provider.objects.get(pk=obj.pk).approval_status

        super().save_model(request, obj, form, change)

        if not change or old_status != obj.approval_status:
            ApprovalRecord.objects.create(
                provider=obj,
                status=obj.approval_status,
                decided_by=request.user,
                notes="Provider approval status updated from admin.",
            )


@admin.register(ApprovalRecord)
class ApprovalRecordAdmin(admin.ModelAdmin):
    list_display = ("provider", "status", "decided_by", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("provider__user__username", "notes")


@admin.register(ServiceCatalogueLog)
class ServiceCatalogueLogAdmin(admin.ModelAdmin):
    list_display = ("service", "action", "performed_by", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("service__name", "details")


@admin.register(SystemReport)
class SystemReportAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user_count",
        "provider_count",
        "booking_count",
        "paid_transaction_count",
        "total_revenue",
        "average_rating",
        "generated_at",
    )
    readonly_fields = (
        "user_count",
        "provider_count",
        "booking_count",
        "paid_transaction_count",
        "total_revenue",
        "average_rating",
        "generated_at",
    )

    def save_model(self, request, obj, form, change):
        obj.generated_by = request.user
        obj.user_count = User.objects.count()
        obj.provider_count = Provider.objects.count()
        obj.booking_count = ServiceRequest.objects.count()
        obj.paid_transaction_count = ServiceRequest.objects.filter(payment_status="paid").count()
        obj.total_revenue = ServiceRequest.objects.filter(payment_status="paid").aggregate(
            total=Sum("amount_paid")
        )["total"] or 0
        obj.average_rating = ServiceRequest.objects.exclude(rating__isnull=True).aggregate(
            avg=Avg("rating")
        )["avg"]
        super().save_model(request, obj, form, change)
