from rest_framework import serializers
from apps.reports.models import Report
from django.conf import settings
from .models import Assignment

class AssignmentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    report = serializers.PrimaryKeyRelatedField(
        queryset=Report.objects.all()  # ✅ obligatoire
    )

    class Meta:
        model = Assignment
        fields = ['id', 'user', 'report', 'statut', 'date_assigne', 'date_echeance']
        read_only_fields = ['id', 'user', 'date_assigne']
