from django.contrib import admin
from .models import ServiceRequest, SearchHistory, ProviderSelection


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "service",
        "provider",
        "status",
        "payment_status",
        "requested_at",
    )

    list_filter = (
        "status",
        "payment_status",
    )

    search_fields = (
        "user__username",
        "service__name",
    )


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "service",
        "location",
        "results_count",
        "searched_at",
    )

    list_filter = ("searched_at",)

    search_fields = (
        "user__username",
        "service__name",
    )


@admin.register(ProviderSelection)
class ProviderSelectionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "provider",
        "service",
        "selected_at",
    )

    list_filter = ("selected_at",)

    search_fields = (
        "user__username",
        "provider__user__username",
    )