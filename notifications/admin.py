from django.contrib import admin
from OrderManagement.models import Notification, NotificationLog


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "is_read", "order", "created_at")
    list_filter = ("type", "is_read", "created_at")
    search_fields = ("title", "message", "order__id")
    readonly_fields = ("created_at",)
    list_editable = ("is_read",)
    ordering = ("-created_at",)

    actions = ["mark_as_read", "mark_as_unread"]

    @admin.action(description="Mark selected as read")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} notifications marked as read.")

    @admin.action(description="Mark selected as unread")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f"{queryset.count()} notifications marked as unread.")


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("order", "channel", "status", "created_at", "short_error")
    list_filter = ("channel", "status", "created_at")
    search_fields = ("order__id", "error")
    readonly_fields = ("order", "channel", "status", "error", "created_at")
    ordering = ("-created_at",)

    # Prevent accidental edits to logs
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def short_error(self, obj):
        return obj.error[:60] + "..." if len(obj.error) > 60 else obj.error or "—"

    short_error.short_description = "Error"