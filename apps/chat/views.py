from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import models
from django.db.models import Max, Q
from .models import Message
from .serializers import MessageSerializer, MessageCreateSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

# Lister tous les messages globaux ou privés pour l'utilisateur
class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Messages globaux + messages où l'user est destinataire ou expéditeur
        return Message.objects.filter(
            models.Q(recipient=None) | models.Q(sender=user) | models.Q(recipient=user)
        ).order_by("created_at")

# Messages pour une conversation spécifique
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def conversation_messages(request, user_id):
    """Récupérer les messages entre l'utilisateur actuel et un utilisateur spécifique"""
    user = request.user
    other_user = User.objects.get(id=user_id)
    
    messages = Message.objects.filter(
        (Q(sender=user) & Q(recipient=other_user)) |
        (Q(sender=other_user) & Q(recipient=user))
    ).order_by('created_at')
    
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)

# Liste des conversations
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def conversations_list(request):
    """Récupérer la liste des conversations de l'utilisateur"""
    user = request.user
    
    # Récupérer les derniers messages pour chaque conversation
    conversations = Message.objects.filter(
        Q(sender=user) | Q(recipient=user),
        recipient__isnull=False  # Exclure les messages globaux
    ).values(
        'sender_id',
        'recipient_id'
    ).annotate(
        last_message_time=Max('created_at')
    ).order_by('-last_message_time')
    
    result = []
    for conv in conversations:
        # Déterminer l'autre utilisateur
        other_user_id = conv['recipient_id'] if conv['sender_id'] == user.id else conv['sender_id']
        other_user = User.objects.get(id=other_user_id)
        
        # Récupérer le dernier message
        last_message = Message.objects.filter(
            Q(sender=user, recipient=other_user) | Q(sender=other_user, recipient=user)
        ).order_by('-created_at').first()
        
        # Compter les messages non lus
        unread_count = Message.objects.filter(
            sender=other_user,
            recipient=user,
            # TODO: Ajouter un champ is_read pour gérer la lecture
        ).count()
        
        result.append({
            'id': other_user_id,
            'user': {
                'id': other_user.id,
                'email': other_user.email,
                'nom': other_user.nom,
                'photo': other_user.photo.url if other_user.photo else None,
            },
            'lastMessage': MessageSerializer(last_message).data if last_message else None,
            'unreadCount': unread_count,
            'isOnline': False,  # TODO: Implémenter avec WebSocket
        })
    
    return Response(result)

# Créer un message (global ou privé)
class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
