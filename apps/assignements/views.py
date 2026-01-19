from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Assignment
from .serializers import AssignmentSerializer

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['statut', 'user', 'report']
    search_fields = ['report__description', 'user__nom']
    ordering_fields = ['date_assigne', 'date_echeance', 'statut']
    ordering = ['-date_assigne']
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_assignments(self, request):
        assignments = Assignment.objects.filter(user=request.user)
        page = self.paginate_queryset(assignments)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_in_progress(self, request, pk=None):
        assignment = self.get_object()
        assignment.statut = 'en_cours'
        assignment.save()
        
        # Update report status
        assignment.report.statut = 'en_cours'
        assignment.report.save()
        
        return Response({
            'status': 'in_progress',
            'assignment_status': assignment.statut,
            'report_status': assignment.report.statut
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_completed(self, request, pk=None):
        assignment = self.get_object()
        assignment.statut = 'termine'
        assignment.save()
        
        # Update report status
        assignment.report.statut = 'resolu'
        assignment.report.save()
        
        return Response({
            'status': 'completed',
            'assignment_status': assignment.statut,
            'report_status': assignment.report.statut
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_cancelled(self, request, pk=None):
        assignment = self.get_object()
        assignment.statut = 'annule'
        assignment.save()
        
        # Update report status
        assignment.report.statut = 'en_attente'
        assignment.report.save()
        
        return Response({
            'status': 'cancelled',
            'assignment_status': assignment.statut,
            'report_status': assignment.report.statut
        })
