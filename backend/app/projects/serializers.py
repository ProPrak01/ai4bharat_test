"""
Serializers for Project and ProjectMember models.
"""
from rest_framework import serializers
from django.db import transaction
from .models import Project, ProjectMember
from users.serializers import UserSerializer


class ProjectMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for ProjectMember model.
    """
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ProjectMember
        fields = (
            'id', 'user', 'user_id', 'role', 'joined_at'
        )
        read_only_fields = ('id', 'joined_at')

    def validate_user_id(self, value):
        """Validate user exists."""
        from users.models import User
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        return value

    def validate(self, attrs):
        """Validate project membership."""
        user_id = attrs.get('user_id')
        project = self.context.get('project')
        
        if project:
            # Check if user is already a member
            if ProjectMember.objects.filter(project=project, user_id=user_id).exists():
                raise serializers.ValidationError(
                    "User is already a member of this project."
                )
            
            # Check if user is the project owner
            if project.owner_id == user_id:
                raise serializers.ValidationError(
                    "Project owner cannot be added as a member."
                )
        
        return attrs


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model.
    """
    owner = UserSerializer(read_only=True)
    members = ProjectMemberSerializer(many=True, read_only=True)
    member_count = serializers.ReadOnlyField(source='get_member_count')
    issue_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = (
            'id', 'name', 'description', 'owner', 'members',
            'member_count', 'issue_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at')

    def get_issue_count(self, obj):
        """Get total number of issues in the project."""
        return obj.issues.count()

    def validate_name(self, value):
        """Validate project name."""
        if not value.strip():
            raise serializers.ValidationError("Project name cannot be empty.")
        return value.strip()

    def create(self, validated_data):
        """Create new project with current user as owner."""
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class ProjectListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for project lists.
    """
    owner = serializers.StringRelatedField()
    member_count = serializers.ReadOnlyField(source='get_member_count')
    issue_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = (
            'id', 'name', 'description', 'owner', 
            'member_count', 'issue_count', 'created_at', 'updated_at'
        )

    def get_issue_count(self, obj):
        """Get total number of issues in the project."""
        return obj.issues.count()


class ProjectDetailSerializer(ProjectSerializer):
    """
    Detailed serializer for single project view.
    """
    recent_issues = serializers.SerializerMethodField()
    
    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ('recent_issues',)

    def get_recent_issues(self, obj):
        """Get recent issues in the project."""
        from issues.serializers import IssueListSerializer
        recent_issues = obj.issues.all()[:5]
        return IssueListSerializer(recent_issues, many=True, context=self.context).data


class AddProjectMemberSerializer(serializers.Serializer):
    """
    Serializer for adding members to a project.
    """
    user_id = serializers.IntegerField()
    role = serializers.ChoiceField(
        choices=ProjectMember.ROLE_CHOICES,
        default='member'
    )

    def validate_user_id(self, value):
        """Validate user exists."""
        from users.models import User
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        return value

    def validate(self, attrs):
        """Validate membership addition."""
        user_id = attrs.get('user_id')
        project = self.context.get('project')
        
        if project:
            # Check if user is already a member
            if ProjectMember.objects.filter(project=project, user_id=user_id).exists():
                raise serializers.ValidationError(
                    "User is already a member of this project."
                )
            
            # Check if user is the project owner
            if project.owner_id == user_id:
                raise serializers.ValidationError(
                    "Project owner cannot be added as a member."
                )
        
        return attrs

    def save(self):
        """Add member to project."""
        project = self.context['project']
        return ProjectMember.objects.create(
            project=project,
            user_id=self.validated_data['user_id'],
            role=self.validated_data['role']
        )


class UpdateProjectMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for updating project member role.
    """
    class Meta:
        model = ProjectMember
        fields = ('role',)

    def validate_role(self, value):
        """Validate role change."""
        if not value:
            raise serializers.ValidationError("Role cannot be empty.")
        return value