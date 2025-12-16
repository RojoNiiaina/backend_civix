from rest_framework import serializers
from .models import User

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nom', 'email', 'role', 'statut', 'date_inscription']
        read_only_fields = ['id', 'date_inscription']


User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('id', 'nom', 'email', 'password', 'role', 'statut')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            nom=validated_data['nom'],
            role=validated_data.get('role', 'user'),
            statut=validated_data.get('statut', 'active')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
