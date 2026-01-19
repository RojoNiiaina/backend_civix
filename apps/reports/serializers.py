from rest_framework import serializers
from apps.users.serializers import UserSerializer
from .models import Report, Like
from django.conf import settings

class ReportSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    image = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id', 'user',
            'description', 'lieu', 'image',
            'statut', 'created_at', 'like', 'like_count', 'is_liked'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'like', 'like_count', 'is_liked']

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            # Fallback si pas de request dans le contexte
            return f"http://localhost:8000{obj.image.url}"
        return None

    def get_like_count(self, obj):
        """Retourne le nombre total de likes"""
        return obj.likes.count()

    def get_is_liked(self, obj):
        """Vérifie si l'utilisateur actuel a liké ce report"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, report=obj).exists()
        return False
