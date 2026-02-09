from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Comment
from .serializers import CommentSerializer
from apps.notification.models import Notification

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report', 'user']

    
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        comment = serializer.save(user=self.request.user)
        
        # Create notification for the report owner (if not the same user)
        if comment.report.user != self.request.user:
            Notification.objects.create(
                report=comment.report,
                user=comment.report.user,
                message=f"Your report has been commented by {self.request.user.nom}"
            )
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_comments(self, request):
        comments = Comment.objects.filter(user=request.user)
        page = self.paginate_queryset(comments)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_as_read(self, request, pk=None):
        comment = self.get_object()
        # For future implementation if we add read/unread functionality
        return Response({'status': 'comment marked as processed'})
