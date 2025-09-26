"""
User model extending Django's built-in AbstractUser.
Provides custom user functionality for the bug reporting system.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending AbstractUser.

    Adds email uniqueness constraint and timestamp tracking to the default User model.
    This model serves as the central user entity for authentication and authorization
    across the bug reporting system.

    Attributes:
        email (EmailField): Unique email address for the user
        created_at (DateTimeField): Timestamp when the user account was created
        updated_at (DateTimeField): Timestamp when the user account was last modified
    """

    # Make email field unique (overrides AbstractUser's email field)
    email = models.EmailField(
        unique=True,
        help_text="Email address must be unique across all users"
    )

    # Timestamp fields for audit trail
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the user account was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the user account was last updated"
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        """String representation of the user."""
        return self.username

    def get_full_name(self):
        """Return the full name of the user."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username
