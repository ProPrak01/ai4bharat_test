"""
Django admin configuration for Issue and Comment models.
Provides comprehensive bug tracking and comment management interface.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Issue, Comment


class CommentInline(admin.StackedInline):
    """
    Inline admin for Comment within Issue admin.
    Allows viewing and managing comments directly from the issue page.
    """
    model = Comment
    extra = 0
    fields = ('author', 'content')
    readonly_fields = ('author', 'created_at')
    autocomplete_fields = ['author']

    def has_add_permission(self, request, obj=None):
        """Allow adding comments only if user has change permission."""
        return request.user.has_perm('issues.add_comment')


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    """
    Admin interface for Issue model.

    Provides comprehensive issue management with status tracking,
    assignment capabilities, and inline comment management.
    """

    # Display configuration
    list_display = (
        'title', 'project', 'status', 'priority',
        'reporter', 'assignee', 'get_comment_count', 'created_at'
    )
    list_filter = (
        'status', 'priority', 'created_at',
        'updated_at', 'project'
    )
    search_fields = (
        'title', 'description',
        'reporter__username', 'assignee__username',
        'project__name'
    )
    autocomplete_fields = ['project', 'reporter', 'assignee']
    list_editable = ('status', 'priority', 'assignee')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    # Read-only fields
    readonly_fields = ('created_at', 'updated_at', 'reporter')

    # Fieldset organization
    fieldsets = (
        ('Issue Information', {
            'fields': ('title', 'description', 'project')
        }),
        ('Assignment & Status', {
            'fields': ('status', 'priority', 'reporter', 'assignee')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    # Inline editing
    inlines = [CommentInline]

    # Actions
    actions = [
        'mark_as_open', 'mark_as_in_progress',
        'mark_as_closed', 'set_high_priority'
    ]

    # Custom display methods
    def get_status_display(self, obj):
        """Display status with color coding."""
        colors = {
            'open': 'orange',
            'in_progress': 'blue',
            'closed': 'green'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    get_status_display.short_description = 'Status'
    get_status_display.admin_order_field = 'status'

    def get_priority_display(self, obj):
        """Display priority with color coding."""
        colors = {
            'low': 'gray',
            'medium': 'orange',
            'high': 'red',
            'critical': 'darkred'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold">{}</span>',
            colors.get(obj.priority, 'black'),
            obj.get_priority_display()
        )
    get_priority_display.short_description = 'Priority'
    get_priority_display.admin_order_field = 'priority'

    # Action methods
    def mark_as_open(self, request, queryset):
        """Mark selected issues as open."""
        count = queryset.update(status='open')
        self.message_user(request, f"{count} issue(s) marked as open.")
    mark_as_open.short_description = "Mark as Open"

    def mark_as_in_progress(self, request, queryset):
        """Mark selected issues as in progress."""
        count = queryset.update(status='in_progress')
        self.message_user(request, f"{count} issue(s) marked as in progress.")
    mark_as_in_progress.short_description = "Mark as In Progress"

    def mark_as_closed(self, request, queryset):
        """Mark selected issues as closed."""
        count = queryset.update(status='closed')
        self.message_user(request, f"{count} issue(s) marked as closed.")
    mark_as_closed.short_description = "Mark as Closed"

    def set_high_priority(self, request, queryset):
        """Set selected issues to high priority."""
        count = queryset.update(priority='high')
        self.message_user(request, f"{count} issue(s) set to high priority.")
    set_high_priority.short_description = "Set High Priority"

    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related."""
        return super().get_queryset(request).select_related(
            'project', 'reporter', 'assignee'
        ).prefetch_related('comments')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for Comment model.

    Provides comment management with issue context and author tracking.
    """

    # Display configuration
    list_display = (
        'get_short_content', 'issue', 'author', 'created_at'
    )
    list_filter = ('created_at', 'updated_at', 'issue__project')
    search_fields = (
        'content', 'issue__title',
        'author__username', 'issue__project__name'
    )
    autocomplete_fields = ['issue', 'author']
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    # Read-only fields
    readonly_fields = ('created_at', 'updated_at')

    # Fieldset organization
    fieldsets = (
        ('Comment Information', {
            'fields': ('issue', 'author', 'content')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_short_content(self, obj):
        """Display truncated content for list view."""
        content = obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return mark_safe(f'<span title="{obj.content}">{content}</span>')
    get_short_content.short_description = 'Content'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'issue', 'author', 'issue__project'
        )
