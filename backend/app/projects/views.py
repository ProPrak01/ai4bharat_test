"""
API views for project management.
"""
from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import models
from .models import Project, ProjectMember
from .serializers import (
    ProjectSerializer,
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectMemberSerializer,
    AddProjectMemberSerializer,
    UpdateProjectMemberSerializer
)
from api.permissions import IsOwnerOrReadOnly, IsProjectOwnerOrAdminOrReadOnly, CanManageProjectMembers


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project model with full CRUD operations.
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['owner']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return projects where user is owner or member."""
        user = self.request.user
        return Project.objects.filter(
            models.Q(owner=user) | 
            models.Q(members__user=user)
        ).distinct().select_related('owner').prefetch_related('members__user')

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ProjectListSerializer
        elif self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectSerializer

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get project members."""
        project = self.get_object()
        members = project.members.all()
        serializer = ProjectMemberSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[CanManageProjectMembers])
    def add_member(self, request, pk=None):
        """Add a member to the project."""
        project = self.get_object()
        serializer = AddProjectMemberSerializer(
            data=request.data,
            context={'project': project}
        )
        serializer.is_valid(raise_exception=True)
        member = serializer.save()
        
        return Response(
            ProjectMemberSerializer(member).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['delete'], url_path='members/(?P<user_id>[^/.]+)', 
            permission_classes=[CanManageProjectMembers])
    def remove_member(self, request, pk=None, user_id=None):
        """Remove a member from the project."""
        project = self.get_object()
        member = get_object_or_404(ProjectMember, project=project, user_id=user_id)
        member.delete()
        
        return Response(
            {'message': 'Member removed successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=['patch'], url_path='members/(?P<user_id>[^/.]+)',
            permission_classes=[CanManageProjectMembers])
    def update_member_role(self, request, pk=None, user_id=None):
        """Update member role."""
        project = self.get_object()
        member = get_object_or_404(ProjectMember, project=project, user_id=user_id)
        serializer = UpdateProjectMemberSerializer(member, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(ProjectMemberSerializer(member).data)


    def get_project(self):
        """Helper method to get project for permissions."""
        return self.get_object()
