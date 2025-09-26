"""
Main API URL configuration with versioning.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# Import viewsets
from projects.views import ProjectViewSet
from issues.views import IssueViewSet, CommentViewSet, AllIssuesViewSet, MyIssuesViewSet

# Main router
router = DefaultRouter()

# Register main endpoints
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'issues', AllIssuesViewSet, basename='all_issues')
router.register(r'my-issues', MyIssuesViewSet, basename='my_issues')

# Nested routers for project-specific resources
projects_router = routers.NestedDefaultRouter(router, r'projects', lookup='project')
projects_router.register(r'issues', IssueViewSet, basename='project-issues')

# Nested router for issue comments
issues_router = routers.NestedDefaultRouter(projects_router, r'issues', lookup='issue')
issues_router.register(r'comments', CommentViewSet, basename='issue-comments')

urlpatterns = [
    # API documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Authentication endpoints
    path('auth/', include('users.urls')),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Main API routes
    path('', include(router.urls)),
    path('', include(projects_router.urls)),
    path('', include(issues_router.urls)),
]