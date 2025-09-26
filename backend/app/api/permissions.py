"""
Custom permissions for the bug reporting system.
"""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.owner == request.user


class IsProjectMemberOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow project members to edit project-related objects.
    """
    def has_permission(self, request, view):
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # For create/write operations, check if user is project member
        if request.user.is_authenticated:
            # Get project from view context for create operations
            project = getattr(view, 'get_project', lambda: None)()
            if project:
                return project.is_member(request.user)
            return True  # Allow if no project context (will be checked in has_object_permission)

        return False

    def has_object_permission(self, request, view, obj):
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Write permissions for project members only
        if hasattr(obj, 'project'):
            return obj.project.is_member(request.user)

        return False


class IsProjectOwnerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission for project management - only owner and admins can modify.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Get the project
        project = obj if hasattr(obj, 'owner') else obj.project

        # Write permissions for project owner
        if project.owner == request.user:
            return True

        # Write permissions for project admins
        if hasattr(project, 'members'):
            member = project.members.filter(user=request.user, role='admin').first()
            return member is not None

        return False


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of comments to edit them.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Write permissions are only allowed to the author of the comment
        return obj.author == request.user


class IsProjectMember(permissions.BasePermission):
    """
    Permission to check if user is a member of the project.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Get project from view context
        project = getattr(view, 'get_project', lambda: None)()
        if project:
            return project.is_member(request.user)
        
        return True

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Get project from object
        project = obj if hasattr(obj, 'owner') else getattr(obj, 'project', None)
        if project:
            return project.is_member(request.user)
        
        return True


class CanAssignIssues(permissions.BasePermission):
    """
    Permission to check if user can assign issues in a project.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Get project from view context
        project = getattr(view, 'get_project', lambda: None)()
        if project:
            # Project owner can always assign
            if project.owner == request.user:
                return True
            
            # Project admins can assign
            member = project.members.filter(user=request.user, role='admin').first()
            return member is not None
        
        return False


class CanManageProjectMembers(permissions.BasePermission):
    """
    Permission to check if user can manage project members.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Get project from view context
        project = getattr(view, 'get_project', lambda: None)()
        if project:
            # Only project owner can manage members
            return project.owner == request.user
        
        return False

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # For project member objects, check if user is project owner
        if hasattr(obj, 'project'):
            return obj.project.owner == request.user
        
        return False