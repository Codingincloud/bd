from django.contrib import admin
from .models import AdminProfile, SystemNotification

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'department', 'created_at']
    search_fields = ['name', 'email']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notification_type', 'target_audience', 'is_active', 'created_at']
    list_filter = ['notification_type', 'target_audience', 'is_active']
    search_fields = ['title', 'message']
