from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class LiveStream(models.Model):
    """
    Modèle pour les streams live
    """
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('live', 'En direct'),
        ('ended', 'Terminé'),
        ('cancelled', 'Annulé'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    streamer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="live_streams")
    stream_key = models.CharField(max_length=100, unique=True)
    thumbnail = models.ImageField(upload_to='live/thumbnails/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    viewer_count = models.PositiveIntegerField(default=0)
    max_viewers = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_at"]
    
    def __str__(self):
        try:
            if hasattr(self.streamer, 'nom') and self.streamer.nom:
                return f"{self.title} - {self.streamer.nom}"
            else:
                return f"{self.title} - {self.streamer.email}"
        except Exception as e:
            print(f"DEBUG: Error in LiveStream.__str__: {e}")
            return f"{self.title} - User {self.streamer.id}"
    
    @property
    def duration(self):
        if self.started_at and self.ended_at:
            return self.ended_at - self.started_at
        elif self.started_at:
            return timezone.now() - self.started_at
        return None

class LiveMessage(models.Model):
    """
    Messages du chat live
    """
    stream = models.ForeignKey(LiveStream, on_delete=models.CASCADE, related_name="live_messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["created_at"]
    
    def __str__(self):
        try:
            if hasattr(self.user, 'nom') and self.user.nom:
                return f"{self.user.nom}: {self.content[:50]}"
            else:
                return f"{self.user.email}: {self.content[:50]}"
        except Exception as e:
            print(f"DEBUG: Error in LiveMessage.__str__: {e}")
            return f"User {self.user.id}: {self.content[:50]}"

class LiveViewer(models.Model):
    """
    Suivi des viewers pour les statistiques
    """
    stream = models.ForeignKey(LiveStream, on_delete=models.CASCADE, related_name="live_viewers")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # null pour anonymous
    session_id = models.CharField(max_length=100, blank=True)  # pour les viewers anonymes
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ["-joined_at"]
    
    def __str__(self):
        try:
            if self.user and hasattr(self.user, 'nom') and self.user.nom:
                identifier = self.user.nom
            elif self.user:
                identifier = self.user.email
            else:
                identifier = self.session_id[:8] if self.session_id else "Anonymous"
            return f"{identifier} - {self.stream.title}"
        except Exception as e:
            print(f"DEBUG: Error in LiveViewer.__str__: {e}")
            return f"Unknown - {self.stream.title}"
