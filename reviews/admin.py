from django.contrib import admin

# Register your models here.
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "service_request",
        "reviewer",
        "rating",
        "created_at",
    )

    list_filter = ("rating", "created_at")

    search_fields = (
        "reviewer__username",
        "service_request__id",
    )