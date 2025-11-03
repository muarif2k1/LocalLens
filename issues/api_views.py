from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Issue, IssueCategory, IssueComment, IssueUpvote, AffectedUser
from .serializers import (
    IssueSerializer, IssueCategorySerializer, 
    IssueCommentSerializer, IssueMapSerializer
)

class IssueCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IssueCategory.objects.all()
    serializer_class = IssueCategorySerializer


class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.filter(is_duplicate=False).select_related('category', 'reporter')
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'ward', 'zone']
    search_fields = ['title', 'description', 'address']
    ordering_fields = ['created_at', 'upvotes', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by privacy
        if not self.request.user.is_authenticated or not self.request.user.is_authority:
            queryset = queryset.filter(privacy='public')
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upvote(self, request, pk=None):
        issue = self.get_object()
        upvote, created = IssueUpvote.objects.get_or_create(
            issue=issue, 
            user=request.user
        )
        
        if not created:
            upvote.delete()
            issue.upvotes -= 1
            issue.save()
            return Response({
                'status': 'removed',
                'upvotes': issue.upvotes
            })
        else:
            issue.upvotes += 1
            issue.save()
            return Response({
                'status': 'added',
                'upvotes': issue.upvotes
            })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_affected(self, request, pk=None):
        issue = self.get_object()
        affected, created = AffectedUser.objects.get_or_create(
            issue=issue,
            user=request.user
        )
        
        if not created:
            affected.delete()
            return Response({
                'status': 'removed',
                'count': issue.affected_users.count()
            })
        else:
            return Response({
                'status': 'added',
                'count': issue.affected_users.count()
            })
    
    @action(detail=False, methods=['get'])
    def map_data(self, request):
        issues = self.filter_queryset(self.get_queryset())
        serializer = IssueMapSerializer(issues, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        queryset = self.get_queryset()
        stats = {
            'total': queryset.count(),
            'pending': queryset.filter(status='pending').count(),
            'in_progress': queryset.filter(status='in_progress').count(),
            'resolved': queryset.filter(status='resolved').count(),
            'by_category': list(
                queryset.values('category__name')
                .annotate(count=models.Count('id'))
                .order_by('-count')
            )
        }
        return Response(stats)


class IssueCommentViewSet(viewsets.ModelViewSet):
    queryset = IssueComment.objects.select_related('user', 'issue')
    serializer_class = IssueCommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['issue']
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
