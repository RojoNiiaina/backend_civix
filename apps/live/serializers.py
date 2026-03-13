from rest_framework import serializers
from .models import LiveStream, LiveMessage, LiveViewer
from django.contrib.auth import get_user_model

User = get_user_model()

class LiveStreamSerializer(serializers.ModelSerializer):
    streamer_info = serializers.SerializerMethodField()
    is_live = serializers.BooleanField(read_only=True)
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = LiveStream
        fields = [
            'id', 'title', 'description', 'streamer_info', 'stream_key', 'thumbnail_url', 'status', 
            'started_at', 'ended_at', 'viewer_count', 'max_viewers', 
            'created_at', 'updated_at', 'is_live'
        ]
        read_only_fields = ['stream_key', 'viewer_count', 'max_viewers', 'started_at', 'ended_at', 'streamer', 'thumbnail']
    
    def get_streamer_info(self, obj):
        try:
            user = obj.streamer
            photo_url = None
            if user.photo:
                try:
                    request = self.context.get('request')
                    if request:
                        photo_url = request.build_absolute_uri(user.photo.url)
                    else:
                        photo_url = user.photo.url
                except Exception as e:
                    print(f"DEBUG: Error getting photo URL: {e}")
                    photo_url = None
            
            return {
                'id': user.id,
                'nom': getattr(user, 'nom', None) or user.email,
                'email': user.email,
                'photo': photo_url
            }
        except Exception as e:
            print(f"DEBUG: Error getting streamer info: {e}")
            return {
                'id': obj.streamer.id,
                'nom': obj.streamer.email,
                'email': obj.streamer.email,
                'photo': None
            }
    
    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            try:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.thumbnail.url)
                else:
                    return obj.thumbnail.url
            except Exception as e:
                print(f"DEBUG: Error getting thumbnail URL: {e}")
                return None
        return None
    
    def get_is_live(self, obj):
        return obj.status == 'live'

class LiveMessageSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = LiveMessage
        fields = ['id', 'stream', 'user', 'user_name', 'user_photo_url', 'content', 'created_at']
        read_only_fields = ['user']
    
    def get_user_name(self, obj):
        try:
            if hasattr(obj.user, 'nom') and obj.user.nom:
                return obj.user.nom
            else:
                return obj.user.email
        except Exception:
            return f"User {obj.user.id}"
    
    def get_user_photo_url(self, obj):
        try:
            if obj.user.photo:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.user.photo.url)
                else:
                    return obj.user.photo.url
            return None
        except Exception:
            return None

class LiveViewerSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = LiveViewer
        fields = ['id', 'stream', 'user', 'user_name', 'session_id', 'joined_at', 'left_at']
        read_only_fields = ['joined_at', 'left_at']
    
    def get_user_name(self, obj):
        try:
            if obj.user and hasattr(obj.user, 'nom') and obj.user.nom:
                return obj.user.nom
            elif obj.user:
                return obj.user.email
            else:
                return obj.session_id[:8] if obj.session_id else "Anonymous"
        except Exception:
            return "Unknown"
