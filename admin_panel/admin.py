from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import AdminProfile, SystemNotification

# Enhance the default User admin
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'user_type']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined', 'groups']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    list_per_page = 25
    date_hierarchy = 'date_joined'

    def user_type(self, obj):
        if hasattr(obj, 'donor'):
            return f"Donor ({obj.donor.blood_group})"
        elif hasattr(obj, 'adminprofile'):
            return f"Admin ({obj.adminprofile.department})"
        elif obj.is_superuser:
            return "Superuser"
        elif obj.is_staff:
            return "Staff"
        else:
            return "Regular User"
    user_type.short_description = 'User Type'

# Unregister the default User admin and register our enhanced version
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'department', 'contact_no', 'user_username', 'created_at']
    list_filter = ['department', 'created_at']
    search_fields = [
        'name', 'email', 'contact_no', 'address', 'department',
        'user__username', 'user__first_name', 'user__last_name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    date_hierarchy = 'created_at'
    ordering = ['name']

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Username'
    user_username.admin_order_field = 'user__username'

    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'name', 'email', 'contact_no', 'photo')
        }),
        ('Professional Information', {
            'fields': ('department', 'address')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(SystemNotification)
class SystemNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notification_type', 'target_audience', 'is_active', 'priority', 'created_at']
    list_filter = ['notification_type', 'target_audience', 'is_active', 'priority', 'created_at']
    search_fields = ['title', 'message', 'action_url']
    readonly_fields = ['created_at']
    list_per_page = 25
    date_hierarchy = 'created_at'
    ordering = ['-created_at', '-priority']

    fieldsets = (
        ('Notification Content', {
            'fields': ('title', 'message', 'notification_type')
        }),
        ('Targeting', {
            'fields': ('target_audience', 'priority')
        }),
        ('Settings', {
            'fields': ('is_active', 'action_url')
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
