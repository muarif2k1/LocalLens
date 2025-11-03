from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import IssueViewSet, IssueCategoryViewSet, IssueCommentViewSet

router = DefaultRouter()
router.register(r'issues', IssueViewSet, basename='issue')
router.register(r'categories', IssueCategoryViewSet, basename='category')
router.register(r'comments', IssueCommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]