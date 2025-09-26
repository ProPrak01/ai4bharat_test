"""
Django admin configuration for User model.
Extends Django's built-in UserAdmin with custom fields and functionality.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Admin interface for the custom User model.

    Extends Django's built-in UserAdmin to include timestamp fields
    and improved display options for the bug reporting system.
    """

    # Display configuration
    list_display = (
        'username', 'email', 'get_full_name', 'is_active',
        'is_staff', 'date_joined', 'created_at'
    )
    list_filter = (
        'is_active', 'is_staff', 'is_superuser',
        'created_at', 'date_joined'
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-created_at',)

    # Read-only fields
    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')

    # Custom fieldsets including timestamp information
    fieldsets = UserAdmin.fieldsets + (
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'description': 'Automatically managed timestamp fields'
        }),
    )

    # Actions
    actions = ['activate_users', 'deactivate_users']

    def activate_users(self, request, queryset):
        """Bulk activate selected users."""
        count = queryset.update(is_active=True)
        self.message_user(
            request,
            f"{count} user(s) successfully activated."
        )
    activate_users.short_description = "Activate selected users"

    def deactivate_users(self, request, queryset):
        """Bulk deactivate selected users."""
        count = queryset.update(is_active=False)
        self.message_user(
            request,
            f"{count} user(s) successfully deactivated."
        )
    deactivate_users.short_description = "Deactivate selected users"
