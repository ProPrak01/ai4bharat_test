"""
Django admin configuration for Project-related models.
Provides management interface for projects and their memberships.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Project, ProjectMember


class ProjectMemberInline(admin.TabularInline):
    """
    Inline admin for ProjectMember within Project admin.
    Allows managing project members directly from the project page.
    """
    model = ProjectMember
    extra = 0
    fields = ('user', 'role')
    autocomplete_fields = ['user']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Admin interface for Project model.

    Provides comprehensive project management with inline member editing
    and enhanced display options.
    """

    # Display configuration
    list_display = (
        'name', 'owner', 'get_member_count',
        'issue_count', 'created_at'
    )
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description', 'owner__username')
    autocomplete_fields = ['owner']
    ordering = ('-created_at',)

    # Read-only fields
    readonly_fields = ('created_at', 'updated_at')

    # Fieldset organization
    fieldsets = (
        ('Project Information', {
            'fields': ('name', 'description', 'owner')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    # Inline editing
    inlines = [ProjectMemberInline]

    # Custom methods for display
    def issue_count(self, obj):
        """Display the number of issues in the project."""
        count = obj.issues.count()
        return format_html(
            '<span style="color: {}">{}</span>',
            'red' if count == 0 else 'green',
            count
        )
    issue_count.short_description = 'Issues'
    issue_count.admin_order_field = 'issues__count'

    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related."""
        return super().get_queryset(request).select_related(
            'owner'
        ).prefetch_related('members', 'issues')


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    """
    Admin interface for ProjectMember model.

    Manages project memberships with role-based filtering and validation.
    """

    # Display configuration
    list_display = ('user', 'project', 'role', 'joined_at')
    list_filter = ('role', 'joined_at', 'project')
    search_fields = (
        'user__username', 'user__email',
        'project__name'
    )
    autocomplete_fields = ['user', 'project']
    list_editable = ('role',)
    ordering = ('-joined_at',)

    # Read-only fields
    readonly_fields = ('joined_at',)

    # Fieldset organization
    fieldsets = (
        ('Membership Details', {
            'fields': ('project', 'user', 'role')
        }),
        ('Timestamps', {
            'fields': ('joined_at',),
            'classes': ('collapse',)
        })
    )

    # Actions
    actions = ['promote_to_admin', 'demote_to_member']

    def promote_to_admin(self, request, queryset):
        """Promote selected members to admin role."""
        count = queryset.update(role='admin')
        self.message_user(
            request,
            f"{count} member(s) promoted to admin."
        )
    promote_to_admin.short_description = "Promote to Admin"

    def demote_to_member(self, request, queryset):
        """Demote selected members to regular member role."""
        count = queryset.update(role='member')
        self.message_user(
            request,
            f"{count} member(s) demoted to regular member."
        )
    demote_to_member.short_description = "Demote to Member"

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'user', 'project'
        )
