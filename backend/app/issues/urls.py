"""
URL configuration for issues API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

app_name = 'issues'

# Main router for issues
router = DefaultRouter()
router.register(r'all', views.AllIssuesViewSet, basename='all_issues')
router.register(r'my', views.MyIssuesViewSet, basename='my_issues')
router.register(r'comments', views.CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]