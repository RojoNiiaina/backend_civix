from rest_framework import serializers
from apps.reports.models import Report
from django.conf import settings
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    report = serializers.PrimaryKeyRelatedField(
        queryset=Report.objects.all(),  # ✅ obligatoire
    )

    class Meta:
        model = Comment
        fields = ['id', 'user', 'report', 'contenu', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
