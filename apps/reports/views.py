from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Report, Like
from .serializers import ReportSerializer
from .permissions import IsOwnerOrReadOnly

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['statut']
    search_fields = ['description']
    ordering_fields = ['created_at', 'statut']
    ordering = ['-created_at']
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        Permet à tous les utilisateurs authentifiés de liker, pas seulement le propriétaire.
        """
        if self.action == 'like':
            return [permissions.IsAuthenticated()]
        return [permission() for permission in self.permission_classes]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_reports(self, request):
        """Récupérer tous les reports de l'utilisateur connecté"""
        reports = Report.objects.filter(user=request.user)
        page = self.paginate_queryset(reports)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(reports, many=True)
        return Response(serializer.data)
    
    @action(
    detail=True,
    methods=['patch'],
    permission_classes=[permissions.IsAuthenticated]
    )
    def approve(self, request, pk=None):
        """
        Approuver un report (admin uniquement)
        """
        report = self.get_object()

        if report.statut == "approuve":
            return Response(
                {"detail": "Ce report est déjà approuvé."},
                status=status.HTTP_400_BAD_REQUEST
            )

        report.statut = "approuve"
        report.save()

        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(
    detail=True,
    methods=['patch'],
    permission_classes=[permissions.IsAuthenticated]
    )
    def reject(self, request, pk=None):
        """
        Refuser un report (admin uniquement)
        """
        report = self.get_object()
        report.statut = "rejete"
        report.save()

        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like ou unlike un report"""
        report = self.get_object()
        
        # Vérifier si l'utilisateur a déjà liké ce report
        like_exists = Like.objects.filter(user=request.user, report=report).exists()
        
        if like_exists:
            # Si le like existe, on le supprime (unlike)
            Like.objects.filter(user=request.user, report=report).delete()
            # Le signal mettra à jour automatiquement le compteur
            is_liked = False
        else:
            # Créer un nouveau like
            Like.objects.create(user=request.user, report=report)
            # Le signal mettra à jour automatiquement le compteur
            is_liked = True
        
        # Rafraîchir le report depuis la base de données pour avoir les valeurs à jour
        report.refresh_from_db()
        
        serializer = self.get_serializer(report)
        return Response({
            'is_liked': is_liked,
            'like_count': report.likes.count(),
            'report': serializer.data
        })