"""
Serializers for Issue and Comment models.
"""
from rest_framework import serializers
from django.db import transaction
from .models import Issue, Comment
from users.serializers import UserSerializer
from projects.serializers import ProjectListSerializer


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    """
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = (
            'id', 'content', 'author', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')

    def validate_content(self, value):
        """Validate comment content."""
        if not value.strip():
            raise serializers.ValidationError("Comment content cannot be empty.")
        return value.strip()

    def create(self, validated_data):
        """Create comment with current user as author."""
        validated_data['author'] = self.context['request'].user
        validated_data['issue'] = self.context['issue']
        return super().create(validated_data)


class CommentListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for comment lists.
    """
    author = serializers.StringRelatedField()
    
    class Meta:
        model = Comment
        fields = (
            'id', 'content', 'author', 'created_at', 'updated_at'
        )


class IssueSerializer(serializers.ModelSerializer):
    """
    Serializer for Issue model.
    """
    reporter = UserSerializer(read_only=True)
    assignee = UserSerializer(read_only=True)
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    project = ProjectListSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.ReadOnlyField(source='get_comment_count')
    
    class Meta:
        model = Issue
        fields = (
            'id', 'title', 'description', 'status', 'priority',
            'project', 'reporter', 'assignee', 'assignee_id',
            'comments', 'comment_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'reporter', 'created_at', 'updated_at')

    def validate_title(self, value):
        """Validate issue title."""
        if not value.strip():
            raise serializers.ValidationError("Issue title cannot be empty.")
        return value.strip()

    def validate_assignee_id(self, value):
        """Validate assignee exists and is a project member."""
        if value is None:
            return value
        
        from users.models import User
        try:
            assignee = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Assignee does not exist.")
        
        # Check if assignee is a member of the project
        project = self.context.get('project')
        if project and not project.is_member(assignee):
            raise serializers.ValidationError(
                "Assignee must be a member of the project."
            )
        
        return value

    def create(self, validated_data):
        """Create issue with current user as reporter."""
        assignee_id = validated_data.pop('assignee_id', None)
        validated_data['reporter'] = self.context['request'].user
        validated_data['project'] = self.context['project']
        
        if assignee_id:
            from users.models import User
            validated_data['assignee'] = User.objects.get(id=assignee_id)
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update issue with assignee handling."""
        assignee_id = validated_data.pop('assignee_id', None)
        
        if 'assignee_id' in self.initial_data:  # Check if assignee_id was provided
            if assignee_id is None:
                validated_data['assignee'] = None
            else:
                from users.models import User
                validated_data['assignee'] = User.objects.get(id=assignee_id)
        
        return super().update(instance, validated_data)


class IssueListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for issue lists.
    """
    reporter = serializers.StringRelatedField()
    assignee = serializers.StringRelatedField()
    project_name = serializers.CharField(source='project.name', read_only=True)
    comment_count = serializers.ReadOnlyField(source='get_comment_count')
    
    class Meta:
        model = Issue
        fields = (
            'id', 'title', 'status', 'priority', 'project_name',
            'reporter', 'assignee', 'comment_count', 'created_at', 'updated_at'
        )


class IssueCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating issues.
    """
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Issue
        fields = (
            'title', 'description', 'status', 'priority', 'assignee_id'
        )

    def validate_title(self, value):
        """Validate issue title."""
        if not value.strip():
            raise serializers.ValidationError("Issue title cannot be empty.")
        return value.strip()

    def validate_assignee_id(self, value):
        """Validate assignee exists and is a project member."""
        if value is None:
            return value
        
        from users.models import User
        try:
            assignee = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Assignee does not exist.")
        
        # Check if assignee is a member of the project
        project = self.context.get('project')
        if project and not project.is_member(assignee):
            raise serializers.ValidationError(
                "Assignee must be a member of the project."
            )
        
        return value

    def create(self, validated_data):
        """Create issue with current user as reporter."""
        assignee_id = validated_data.pop('assignee_id', None)
        validated_data['reporter'] = self.context['request'].user
        validated_data['project'] = self.context['project']
        
        if assignee_id:
            from users.models import User
            validated_data['assignee'] = User.objects.get(id=assignee_id)
        
        return super().create(validated_data)


class IssueUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating issues.
    """
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Issue
        fields = (
            'title', 'description', 'status', 'priority', 'assignee_id'
        )

    def validate_title(self, value):
        """Validate issue title."""
        if not value.strip():
            raise serializers.ValidationError("Issue title cannot be empty.")
        return value.strip()

    def validate_assignee_id(self, value):
        """Validate assignee exists and is a project member."""
        if value is None:
            return value
        
        from users.models import User
        try:
            assignee = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Assignee does not exist.")
        
        # Check if assignee is a member of the project
        project = self.instance.project if self.instance else self.context.get('project')
        if project and not project.is_member(assignee):
            raise serializers.ValidationError(
                "Assignee must be a member of the project."
            )
        
        return value

    def update(self, instance, validated_data):
        """Update issue with assignee handling."""
        assignee_id = validated_data.pop('assignee_id', None)
        
        if 'assignee_id' in self.initial_data:  # Check if assignee_id was provided
            if assignee_id is None:
                validated_data['assignee'] = None
            else:
                from users.models import User
                validated_data['assignee'] = User.objects.get(id=assignee_id)
        
        return super().update(instance, validated_data)


class IssueStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating only issue status.
    """
    class Meta:
        model = Issue
        fields = ('status',)

    def validate_status(self, value):
        """Validate status change."""
        if not value:
            raise serializers.ValidationError("Status cannot be empty.")
        return value