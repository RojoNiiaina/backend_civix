from rest_framework import serializers
from apps.users.serializers import UserSerializer
from .models import Report, Like
from django.conf import settings

class ReportSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    image1_url = serializers.SerializerMethodField()
    image2_url = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id', 'user',
            'description', 'lieu', 'image', 'image_url',
            'image1', 'image1_url', 'image2', 'image2_url',
            'statut', 'created_at', 'like', 'like_count', 'is_liked'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'like', 'like_count', 'is_liked', 'image_url', 'image1_url', 'image2_url']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            # Fallback si pas de request dans le contexte
            return f"http://localhost:8000{obj.image.url}"
        return None

    def get_image1_url(self, obj):
        if obj.image1:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image1.url)
            # Fallback si pas de request dans le contexte
            return f"http://localhost:8000{obj.image1.url}"
        return None

    def get_image2_url(self, obj):
        if obj.image2:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image2.url)
            # Fallback si pas de request dans le contexte
            return f"http://localhost:8000{obj.image2.url}"
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
