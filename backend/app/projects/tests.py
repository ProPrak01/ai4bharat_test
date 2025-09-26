"""
Comprehensive tests for Project and ProjectMember models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from projects.models import Project, ProjectMember

User = get_user_model()


class ProjectModelTest(TestCase):
    """Test cases for the Project model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='projectowner',
            email='owner@example.com',
            password='testpass123'
        )
        self.project_data = {
            'name': 'Test Project',
            'description': 'A test project description',
            'owner': self.user
        }

    def test_create_project(self):
        """Test creating a new project."""
        project = Project.objects.create(**self.project_data)
        self.assertEqual(project.name, 'Test Project')
        self.assertEqual(project.description, 'A test project description')
        self.assertEqual(project.owner, self.user)
        self.assertIsNotNone(project.created_at)
        self.assertIsNotNone(project.updated_at)

    def test_project_string_representation(self):
        """Test the string representation of Project."""
        project = Project.objects.create(**self.project_data)
        self.assertEqual(str(project), 'Test Project')

    def test_get_member_count(self):
        """Test get_member_count method."""
        project = Project.objects.create(**self.project_data)
        # Owner counts as 1
        self.assertEqual(project.get_member_count(), 1)

        # Add a member
        member = User.objects.create_user(
            username='member1',
            email='member@example.com',
            password='pass123'
        )
        ProjectMember.objects.create(project=project, user=member)
        self.assertEqual(project.get_member_count(), 2)

    def test_is_member(self):
        """Test is_member method."""
        project = Project.objects.create(**self.project_data)

        # Owner is a member
        self.assertTrue(project.is_member(self.user))

        # Non-member
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='pass123'
        )
        self.assertFalse(project.is_member(other_user))

        # Add as member
        ProjectMember.objects.create(project=project, user=other_user)
        self.assertTrue(project.is_member(other_user))

    def test_project_validation(self):
        """Test project validation."""
        project = Project(
            name='   ',  # Empty after stripping
            description='Test',
            owner=self.user
        )
        with self.assertRaises(ValidationError):
            project.clean()


class ProjectMemberModelTest(TestCase):
    """Test cases for the ProjectMember model."""

    def setUp(self):
        """Set up test data."""
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='pass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.owner
        )
        self.member = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='pass123'
        )

    def test_create_project_member(self):
        """Test creating a project member."""
        membership = ProjectMember.objects.create(
            project=self.project,
            user=self.member,
            role='member'
        )
        self.assertEqual(membership.project, self.project)
        self.assertEqual(membership.user, self.member)
        self.assertEqual(membership.role, 'member')
        self.assertIsNotNone(membership.joined_at)

    def test_project_member_string_representation(self):
        """Test the string representation of ProjectMember."""
        membership = ProjectMember.objects.create(
            project=self.project,
            user=self.member
        )
        expected = f"{self.member.username} - {self.project.name} (member)"
        self.assertEqual(str(membership), expected)

    def test_unique_together_constraint(self):
        """Test that a user can't be added to the same project twice."""
        ProjectMember.objects.create(
            project=self.project,
            user=self.member
        )
        with self.assertRaises(Exception):
            ProjectMember.objects.create(
                project=self.project,
                user=self.member
            )

    def test_owner_cannot_be_member(self):
        """Test that project owner cannot be added as a member."""
        membership = ProjectMember(
            project=self.project,
            user=self.owner,
            role='member'
        )
        with self.assertRaises(ValidationError):
            membership.clean()
