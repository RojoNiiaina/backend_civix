from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['lu', 'user']
    search_fields = ['message']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Users can only see their own notifications
        return Notification.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def unread(self, request):
        notifications = Notification.objects.filter(user=request.user, lu=False)
        page = self.paginate_queryset(notifications)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_all_as_read(self, request):
        notifications = Notification.objects.filter(user=request.user, lu=False)
        count = notifications.count()
        notifications.update(lu=True)
        return Response({
            'status': 'all marked as read',
            'count': count
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.lu = True
        notification.save()
        return Response({
            'status': 'marked as read',
            'notification_id': notification.id
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_as_unread(self, request, pk=None):
        notification = self.get_object()
        notification.lu = False
        notification.save()
        return Response({
            'status': 'marked as unread',
            'notification_id': notification.id
        })
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def count_unread(self, request):
        count = Notification.objects.filter(user=request.user, lu=False).count()
        return Response({'unread_count': count})
