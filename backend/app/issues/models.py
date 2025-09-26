"""
Issue and Comment models for the bug reporting system.
Handles bug reports, issues, and their associated comments.
"""
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings


class Issue(models.Model):
    """
    Issue model representing a bug report or task.

    Issues belong to projects and can be assigned to users for resolution.
    They have status and priority levels to help with organization and workflow.

    Attributes:
        title (CharField): Brief title of the issue (max 200 characters)
        description (TextField): Detailed description of the issue
        status (CharField): Current status of the issue
        priority (CharField): Priority level of the issue
        project (ForeignKey): Project this issue belongs to
        reporter (ForeignKey): User who reported the issue
        assignee (ForeignKey): User assigned to resolve the issue (optional)
        created_at (DateTimeField): Issue creation timestamp
        updated_at (DateTimeField): Last modification timestamp
    """

    # Status choices for issue workflow
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]

    # Priority levels for issue triage
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    title = models.CharField(
        max_length=200,
        help_text="Brief title describing the issue (max 200 characters)"
    )
    description = models.TextField(
        help_text="Detailed description of the issue"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        help_text="Current status of the issue"
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Priority level of the issue"
    )

    # Relationship fields
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='issues',
        help_text="Project this issue belongs to"
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reported_issues',
        help_text="User who reported this issue"
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_issues',
        help_text="User assigned to resolve this issue (optional)"
    )

    # Timestamp fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the issue was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the issue was last updated"
    )

    class Meta:
        db_table = 'issues_issue'
        verbose_name = 'Issue'
        verbose_name_plural = 'Issues'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['assignee']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        """String representation of the issue."""
        return f"{self.title} - {self.project.name}"

    def clean(self):
        """Custom validation for the issue model."""
        super().clean()
        if self.title:
            self.title = self.title.strip()
        if not self.title:
            raise ValidationError({'title': 'Issue title cannot be empty'})

        # Validate assignee is a member of the project
        if self.assignee and hasattr(self, 'project'):
            if not self.project.is_member(self.assignee):
                raise ValidationError({
                    'assignee': 'Assignee must be a member of the project'
                })

    def get_comment_count(self):
        """Return the number of comments on this issue."""
        return self.comments.count()

    def is_open(self):
        """Check if the issue is still open."""
        return self.status == 'open'

    def is_assigned(self):
        """Check if the issue is assigned to someone."""
        return self.assignee is not None


class Comment(models.Model):
    """
    Comment model for issue discussions.

    Comments allow users to discuss and provide updates on issues.
    They maintain an audit trail of all communication related to an issue.

    Attributes:
        content (TextField): The comment text content
        issue (ForeignKey): The issue this comment belongs to
        author (ForeignKey): User who wrote the comment
        created_at (DateTimeField): Comment creation timestamp
        updated_at (DateTimeField): Last modification timestamp
    """

    content = models.TextField(
        help_text="Content of the comment"
    )
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="Issue this comment belongs to"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="User who wrote this comment"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the comment was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the comment was last updated"
    )

    class Meta:
        db_table = 'issues_comment'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['issue']),
            models.Index(fields=['author']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        """String representation of the comment."""
        return f"Comment by {self.author.username} on {self.issue.title}"

    def clean(self):
        """Custom validation for the comment model."""
        super().clean()
        if self.content:
            self.content = self.content.strip()
        if not self.content:
            raise ValidationError({'content': 'Comment content cannot be empty'})

        # Validate author has access to the issue's project
        if hasattr(self, 'issue') and hasattr(self, 'author'):
            if not self.issue.project.is_member(self.author):
                raise ValidationError({
                    'author': 'Author must be a member of the issue project'
                })
