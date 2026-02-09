from rest_framework import serializers
from .models import Notification
from apps.users.serializers import UserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'message','report', 'lu', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
