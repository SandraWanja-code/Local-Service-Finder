from django.contrib import admin
from .models import Provider, ApprovalRecord
from .models import ServiceRequest



@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "location",
        "phone",
        "approval_status",
        "is_available",
    )

    list_filter = ("approval_status", "is_available")
    search_fields = ("user__username", "phone", "location")

    actions = ["approve_providers", "reject_providers"]

    def approve_providers(self, request, queryset):
        for provider in queryset:
            provider.approval_status = "approved"
            provider.save()

            ApprovalRecord.objects.create(
                provider=provider,
                status="approved",
                decided_by=request.user,
                notes="Approved via admin action"
            )

    approve_providers.short_description = "Approve selected providers"

    def reject_providers(self, request, queryset):
        for provider in queryset:
            provider.approval_status = "rejected"
            provider.save()

            ApprovalRecord.objects.create(
                provider=provider,
                status="rejected",
                decided_by=request.user,
                notes="Rejected via admin action"
            )

    reject_providers.short_description = "Reject selected providers"


@admin.register(ApprovalRecord)
class ApprovalRecordAdmin(admin.ModelAdmin):
    list_display = ("provider", "status", "decided_by", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("provider__user__username",)
    
@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "service",
        "user",
        "provider",
        "status",
        "payment_status",
        "requested_at",
    )

    list_filter = ("status", "payment_status")
    search_fields = ("user__username", "service__name", "provider__user__username")    