"""
Project-related models for the bug reporting system.
Handles project management and user memberships.
"""
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings


class Project(models.Model):
    """
    Project model representing a bug tracking project.

    Each project has an owner and can have multiple members with different roles.
    Issues are associated with projects to organize bug reports.

    Attributes:
        name (CharField): Project name (max 200 characters)
        description (TextField): Optional project description
        owner (ForeignKey): User who owns the project
        created_at (DateTimeField): Project creation timestamp
        updated_at (DateTimeField): Last modification timestamp
    """

    name = models.CharField(
        max_length=200,
        help_text="Name of the project (max 200 characters)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description of the project"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        help_text="User who owns this project"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the project was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the project was last updated"
    )

    class Meta:
        db_table = 'projects_project'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        """String representation of the project."""
        return self.name

    def clean(self):
        """Custom validation for the project model."""
        super().clean()
        if self.name:
            self.name = self.name.strip()
        if not self.name:
            raise ValidationError({'name': 'Project name cannot be empty'})

    def get_member_count(self):
        """Return the total number of members in the project."""
        return self.members.count() + 1  # +1 for the owner

    def is_member(self, user):
        """Check if a user is a member of this project."""
        if user == self.owner:
            return True
        return self.members.filter(user=user).exists()


class ProjectMember(models.Model):
    """
    Junction model for project membership with roles.

    Represents the many-to-many relationship between users and projects,
    including the role each user has within the project.

    Attributes:
        project (ForeignKey): The project the user is a member of
        user (ForeignKey): The user who is a member
        role (CharField): The role of the user in the project
        joined_at (DateTimeField): When the user joined the project
    """

    # Role choices for project members
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('admin', 'Admin'),
        ('viewer', 'Viewer'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='members',
        help_text="Project the user is a member of"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_memberships',
        help_text="User who is a member of the project"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='member',
        help_text="Role of the user in the project"
    )
    joined_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the user joined the project"
    )

    class Meta:
        db_table = 'projects_projectmember'
        verbose_name = 'Project Member'
        verbose_name_plural = 'Project Members'
        unique_together = ('project', 'user')
        ordering = ['-joined_at']
        indexes = [
            models.Index(fields=['project', 'user']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        """String representation of the project membership."""
        return f"{self.user.username} - {self.project.name} ({self.role})"

    def clean(self):
        """Custom validation for project membership."""
        super().clean()
        # Ensure the user is not the project owner
        if hasattr(self, 'project') and hasattr(self, 'user'):
            if self.user == self.project.owner:
                raise ValidationError(
                    'Project owner cannot be added as a member'
                )
