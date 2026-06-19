from django.contrib import admin
from .models import AccessLog, ClientProfile, SessionLog, UserManagementLog

# Register your models here.
admin.site.register(ClientProfile)


@admin.register(SessionLog)
class SessionLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "ip_address", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("user__username", "session_key", "ip_address")


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("user__username", "details")


@admin.register(UserManagementLog)
class UserManagementLogAdmin(admin.ModelAdmin):
    list_display = ("admin_user", "target_user", "action", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("admin_user__username", "target_user__username", "notes")
