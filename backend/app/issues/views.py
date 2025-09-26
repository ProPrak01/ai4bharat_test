"""
API views for issue and comment management.
"""
from rest_framework import viewsets, status, permissions, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import models
from .models import Issue, Comment
from projects.models import Project
from .serializers import (
    IssueSerializer,
    IssueListSerializer,
    IssueCreateSerializer,
    IssueUpdateSerializer,
    IssueStatusUpdateSerializer,
    CommentSerializer,
    CommentListSerializer
)
from api.permissions import (
    IsProjectMemberOrReadOnly,
    IsProjectOwnerOrAdminOrReadOnly,
    IsAuthorOrReadOnly,
    IsProjectMember,
    CanAssignIssues
)


class IssueViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Issue model with full CRUD operations.
    """
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'assignee', 'reporter']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return issues from projects where user is member."""
        user = self.request.user
        project_id = self.kwargs.get('project_pk')

        if project_id:
            # Get issues from specific project
            project = get_object_or_404(Project, id=project_id)
            # Allow read access to all, write access only to members
            if self.action in ['list', 'retrieve']:
                return project.issues.all().select_related('project', 'reporter', 'assignee')
            elif not project.is_member(user):
                return Issue.objects.none()
            return project.issues.all().select_related('project', 'reporter', 'assignee')

        # Get issues from all accessible projects
        return Issue.objects.filter(
            models.Q(project__owner=user) |
            models.Q(project__members__user=user)
        ).distinct().select_related('project', 'reporter', 'assignee')

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return IssueListSerializer
        elif self.action == 'create':
            return IssueCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return IssueUpdateSerializer
        elif self.action == 'update_status':
            return IssueStatusUpdateSerializer
        return IssueSerializer

    def get_project(self):
        """Get project from URL or create context."""
        project_id = self.kwargs.get('project_pk')
        if project_id:
            return get_object_or_404(Project, id=project_id)
        return None

    def get_serializer_context(self):
        """Add project to serializer context."""
        context = super().get_serializer_context()
        context['project'] = self.get_project()
        return context

    def perform_create(self, serializer):
        """Create issue with current user as reporter and project from URL."""
        project = self.get_project()
        if not project:
            raise serializers.ValidationError("Project is required to create an issue.")
        serializer.save(reporter=self.request.user, project=project)

    @action(detail=True, methods=['patch'], permission_classes=[CanAssignIssues])
    def update_status(self, request, pk=None, project_pk=None):
        """Update issue status."""
        issue = self.get_object()
        serializer = IssueStatusUpdateSerializer(issue, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(IssueSerializer(issue, context=self.get_serializer_context()).data)

    @action(detail=True, methods=['patch'], permission_classes=[CanAssignIssues])
    def assign(self, request, pk=None, project_pk=None):
        """Assign issue to a user."""
        issue = self.get_object()
        assignee_id = request.data.get('assignee_id')
        
        if assignee_id:
            from users.models import User
            assignee = get_object_or_404(User, id=assignee_id)
            if not issue.project.is_member(assignee):
                return Response(
                    {'error': 'Assignee must be a member of the project.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            issue.assignee = assignee
        else:
            issue.assignee = None
        
        issue.save()
        return Response(IssueSerializer(issue, context=self.get_serializer_context()).data)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None, project_pk=None):
        """Get issue comments."""
        issue = self.get_object()
        comments = issue.comments.all().select_related('author')
        serializer = CommentListSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None, project_pk=None):
        """Add comment to issue."""
        issue = self.get_object()
        serializer = CommentSerializer(
            data=request.data,
            context={'request': request, 'issue': issue}
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED
        )


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Comment model with full CRUD operations.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering = ['created_at']

    def get_queryset(self):
        """Return comments from accessible issues."""
        user = self.request.user
        issue_id = self.kwargs.get('issue_pk')
        project_id = self.kwargs.get('project_pk')
        
        if issue_id and project_id:
            # Get comments from specific issue
            issue = get_object_or_404(Issue, id=issue_id, project_id=project_id)
            if not issue.project.is_member(user):
                return Comment.objects.none()
            return issue.comments.all().select_related('author', 'issue')
        
        # Get comments from all accessible issues
        return Comment.objects.filter(
            models.Q(issue__project__owner=user) |
            models.Q(issue__project__members__user=user)
        ).distinct().select_related('author', 'issue')

    def get_serializer_context(self):
        """Add issue to serializer context."""
        context = super().get_serializer_context()
        issue_id = self.kwargs.get('issue_pk')
        if issue_id:
            project_id = self.kwargs.get('project_pk')
            context['issue'] = get_object_or_404(Issue, id=issue_id, project_id=project_id)
        return context


# Standalone views for general issue management
class AllIssuesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to get all issues across projects for current user.
    """
    serializer_class = IssueListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'assignee', 'reporter', 'project']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return all issues accessible to user."""
        user = self.request.user
        return Issue.objects.filter(
            models.Q(project__owner=user) |
            models.Q(project__members__user=user)
        ).distinct().select_related('project', 'reporter', 'assignee')


class MyIssuesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to get issues assigned to or reported by current user.
    """
    serializer_class = IssueListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'project']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return issues assigned to or reported by current user."""
        user = self.request.user
        return Issue.objects.filter(
            models.Q(assignee=user) | models.Q(reporter=user)
        ).select_related('project', 'reporter', 'assignee')
