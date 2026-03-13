from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
import secrets

from .models import LiveStream, LiveMessage, LiveViewer
from .serializers import LiveStreamSerializer, LiveMessageSerializer, LiveViewerSerializer


class LiveStreamViewSet(viewsets.ModelViewSet):
    queryset = LiveStream.objects.all()
    serializer_class = LiveStreamSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'streamer']
    
    def create(self, request, *args, **kwargs):
        print(f"DEBUG: Create method called")
        print(f"DEBUG: Request user: {request.user}")
        print(f"DEBUG: User is authenticated: {request.user.is_authenticated}")
        print(f"DEBUG: Request data: {request.data}")
        print(f"DEBUG: Request headers: {dict(request.headers)}")
        
        try:
            print(f"DEBUG: About to call super().create")
            response = super().create(request, *args, **kwargs)
            print(f"DEBUG: super().create succeeded")
            print(f"DEBUG: Response data: {response.data}")
            print(f"DEBUG: Response data types: {[(k, type(v)) for k, v in response.data.items()]}")
            return response
        except Exception as e:
            print(f"DEBUG: Exception in create: {e}")
            print(f"DEBUG: Exception type: {type(e)}")
            if hasattr(e, 'detail'):
                print(f"DEBUG: Exception detail: {e.detail}")
            raise
    
    def perform_create(self, serializer):
        # Générer une clé de stream unique
        stream_key = f"stream_{secrets.token_urlsafe(16)}"
        print(f"DEBUG: perform_create called with user: {self.request.user}")
        serializer.save(streamer=self.request.user, stream_key=stream_key)
    
    @action(detail=True, methods=['post'])
    def start_stream(self, request, pk=None):
        """Démarrer un stream"""
        print(f"DEBUG: start_stream appelé pour pk={pk}")
        stream = self.get_object()
        print(f"DEBUG: Stream trouvé: id={stream.id}, status={stream.status}, streamer={stream.streamer}")
        print(f"DEBUG: User demandeur: {request.user}")
        
        if stream.status != 'pending':
            print(f"DEBUG: Erreur - stream status est '{stream.status}', pas 'pending'")
            return Response(
                {'error': f'Ce stream ne peut pas être démarré (statut actuel: {stream.status})'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if stream.streamer != request.user:
            return Response(
                {'error': 'Vous n\'êtes pas autorisé à démarrer ce stream'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        stream.status = 'live'
        stream.started_at = timezone.now()
        stream.save()
        
        return Response({'status': 'Stream démarré'})
    
    @action(detail=True, methods=['post'])
    def end_stream(self, request, pk=None):
        """Terminer un stream"""
        stream = self.get_object()
        if stream.status != 'live':
            return Response(
                {'error': 'Ce stream n\'est pas en direct'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if stream.streamer != request.user:
            return Response(
                {'error': 'Vous n\'êtes pas autorisé de terminer ce stream'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        stream.status = 'ended'
        stream.ended_at = timezone.now()
        stream.save()
        
        return Response({'status': 'Stream terminé'})
    
    @action(detail=False)
    def active_streams(self, request):
        """Liste des streams en direct"""
        streams = self.queryset.filter(status='live')
        serializer = self.get_serializer(streams, many=True)
        return Response(serializer.data)
    
    @action(detail=False)
    def my_streams(self, request):
        """Streams de l'utilisateur connecté"""
        streams = self.queryset.filter(streamer=request.user)
        serializer = self.get_serializer(streams, many=True)
        return Response(serializer.data)
    
    @action(detail=False)
    def by_role(self, request):
        """Filtrer les streams par rôle d'utilisateur (agent/citoyen)"""
        role = request.query_params.get('role')
        if role not in ['agent', 'user']:
            return Response(
                {'error': 'Rôle invalide. Valeurs acceptées: agent, user'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Filtrer les streams par rôle du streamer
        streams = self.queryset.filter(
            streamer__role=role,
            status='live'  # Uniquement les streams en direct
        )
        serializer = self.get_serializer(streams, many=True)
        return Response(serializer.data)


class LiveMessageViewSet(viewsets.ModelViewSet):
    queryset = LiveMessage.objects.all()
    serializer_class = LiveMessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['stream']
    
    def perform_create(self, serializer):
        stream_id = self.request.data.get('stream')
        try:
            stream = LiveStream.objects.get(id=stream_id, status='live')
            serializer.save(user=self.request.user, stream=stream)
        except LiveStream.DoesNotExist:
            raise serializers.ValidationError("Stream non trouvé ou pas en direct")
    
    @action(detail=False)
    def stream_messages(self, request):
        """Messages d'un stream spécifique"""
        stream_id = request.query_params.get('stream_id')
        if not stream_id:
            return Response(
                {'error': 'stream_id requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        messages = self.queryset.filter(stream_id=stream_id)[:50]  # Limiter à 50 messages
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


class LiveViewerViewSet(viewsets.ModelViewSet):
    queryset = LiveViewer.objects.all()
    serializer_class = LiveViewerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['stream']
    
    @action(detail=True, methods=['post'])
    def join_stream(self, request, pk=None):
        """Rejoindre un stream"""
        stream = LiveStream.objects.get(id=pk, status='live')
        
        # Vérifier si l'utilisateur est déjà dans le stream
        existing_viewer = LiveViewer.objects.filter(
            stream=stream, 
            user=request.user, 
            left_at__isnull=True
        ).first()
        
        if existing_viewer:
            return Response({'status': 'Déjà dans le stream'})
        
        # Créer un nouvel enregistrement de viewer
        LiveViewer.objects.create(stream=stream, user=request.user)
        
        # Mettre à jour le compteur de viewers
        stream.viewer_count = LiveViewer.objects.filter(
            stream=stream, 
            left_at__isnull=True
        ).count()
        if stream.viewer_count > stream.max_viewers:
            stream.max_viewers = stream.viewer_count
        stream.save()
        
        return Response({'status': 'Rejoint le stream'})
    
    @action(detail=True, methods=['post'])
    def leave_stream(self, request, pk=None):
        """Quitter un stream"""
        stream = LiveStream.objects.get(id=pk)
        
        viewer = LiveViewer.objects.filter(
            stream=stream, 
            user=request.user, 
            left_at__isnull=True
        ).first()
        
        if viewer:
            viewer.left_at = timezone.now()
            viewer.save()
            
            # Mettre à jour le compteur de viewers
            stream.viewer_count = LiveViewer.objects.filter(
                stream=stream, 
                left_at__isnull=True
            ).count()
            stream.save()
        
        return Response({'status': 'Quitté le stream'})
