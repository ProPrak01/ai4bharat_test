"""
Comprehensive tests for Issue and Comment models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from projects.models import Project, ProjectMember
from issues.models import Issue, Comment

User = get_user_model()


class IssueModelTest(TestCase):
    """Test cases for the Issue model."""

    def setUp(self):
        """Set up test data."""
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='pass123'
        )
        self.reporter = User.objects.create_user(
            username='reporter',
            email='reporter@example.com',
            password='pass123'
        )
        self.assignee = User.objects.create_user(
            username='assignee',
            email='assignee@example.com',
            password='pass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.owner
        )
        # Add assignee as project member
        ProjectMember.objects.create(
            project=self.project,
            user=self.assignee,
            role='member'
        )
        self.issue_data = {
            'title': 'Test Issue',
            'description': 'This is a test issue',
            'project': self.project,
            'reporter': self.reporter,
            'assignee': self.assignee,
            'status': 'open',
            'priority': 'high'
        }

    def test_create_issue(self):
        """Test creating a new issue."""
        issue = Issue.objects.create(**self.issue_data)
        self.assertEqual(issue.title, 'Test Issue')
        self.assertEqual(issue.description, 'This is a test issue')
        self.assertEqual(issue.project, self.project)
        self.assertEqual(issue.reporter, self.reporter)
        self.assertEqual(issue.assignee, self.assignee)
        self.assertEqual(issue.status, 'open')
        self.assertEqual(issue.priority, 'high')
        self.assertIsNotNone(issue.created_at)
        self.assertIsNotNone(issue.updated_at)

    def test_issue_string_representation(self):
        """Test the string representation of Issue."""
        issue = Issue.objects.create(**self.issue_data)
        expected = f"{issue.title} - {self.project.name}"
        self.assertEqual(str(issue), expected)

    def test_issue_defaults(self):
        """Test issue default values."""
        issue = Issue.objects.create(
            title='Minimal Issue',
            description='Test',
            project=self.project,
            reporter=self.reporter
        )
        self.assertEqual(issue.status, 'open')
        self.assertEqual(issue.priority, 'medium')
        self.assertIsNone(issue.assignee)

    def test_get_comment_count(self):
        """Test get_comment_count method."""
        issue = Issue.objects.create(**self.issue_data)
        self.assertEqual(issue.get_comment_count(), 0)

        Comment.objects.create(
            content='Test comment',
            issue=issue,
            author=self.reporter
        )
        self.assertEqual(issue.get_comment_count(), 1)

    def test_is_open(self):
        """Test is_open method."""
        issue = Issue.objects.create(**self.issue_data)
        self.assertTrue(issue.is_open())

        issue.status = 'closed'
        issue.save()
        self.assertFalse(issue.is_open())

    def test_is_assigned(self):
        """Test is_assigned method."""
        issue = Issue.objects.create(**self.issue_data)
        self.assertTrue(issue.is_assigned())

        issue.assignee = None
        issue.save()
        self.assertFalse(issue.is_assigned())

    def test_issue_validation(self):
        """Test issue validation."""
        issue = Issue(
            title='   ',  # Empty after stripping
            description='Test',
            project=self.project,
            reporter=self.reporter
        )
        with self.assertRaises(ValidationError):
            issue.clean()


class CommentModelTest(TestCase):
    """Test cases for the Comment model."""

    def setUp(self):
        """Set up test data."""
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@example.com',
            password='pass123'
        )
        self.author = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='pass123'
        )
        self.project = Project.objects.create(
            name='Test Project',
            owner=self.owner
        )
        # Add author as project member
        ProjectMember.objects.create(
            project=self.project,
            user=self.author,
            role='member'
        )
        self.issue = Issue.objects.create(
            title='Test Issue',
            description='Test description',
            project=self.project,
            reporter=self.owner
        )

    def test_create_comment(self):
        """Test creating a new comment."""
        comment = Comment.objects.create(
            content='This is a test comment',
            issue=self.issue,
            author=self.author
        )
        self.assertEqual(comment.content, 'This is a test comment')
        self.assertEqual(comment.issue, self.issue)
        self.assertEqual(comment.author, self.author)
        self.assertIsNotNone(comment.created_at)
        self.assertIsNotNone(comment.updated_at)

    def test_comment_string_representation(self):
        """Test the string representation of Comment."""
        comment = Comment.objects.create(
            content='Test comment',
            issue=self.issue,
            author=self.author
        )
        expected = f"Comment by {self.author.username} on {self.issue.title}"
        self.assertEqual(str(comment), expected)

    def test_comment_validation(self):
        """Test comment validation."""
        comment = Comment(
            content='   ',  # Empty after stripping
            issue=self.issue,
            author=self.author
        )
        with self.assertRaises(ValidationError):
            comment.clean()

    def test_comment_ordering(self):
        """Test that comments are ordered by creation date."""
        comment1 = Comment.objects.create(
            content='First comment',
            issue=self.issue,
            author=self.author
        )
        comment2 = Comment.objects.create(
            content='Second comment',
            issue=self.issue,
            author=self.author
        )
        comments = Comment.objects.filter(issue=self.issue)
        self.assertEqual(list(comments), [comment1, comment2])
