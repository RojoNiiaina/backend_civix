from rest_framework import serializers
from apps.category.models import Category
from apps.category.serializers import CategorySerializer
from apps.users.serializers import UserSerializer
from .models import Report

class ReportSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        source='category'
    )

    class Meta:
        model = Report
        fields = [
            'id', 'user', 'category', 'category_id',
            'description', 'image',
            'latitude', 'longitude',
            'statut', 'priorite', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
