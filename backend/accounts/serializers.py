from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """Defines serializer for user registration."""

    # Overrides password to validate and write-only
    # Exclude from response
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        # Model to base serialization on
        model = User
        # Fields to include in I/O JSON
        fields = ("id", "username", "email", "password", "role")

    def create(self, validated_data):
        """Called when serializer.save()"""
        # User manager's create_user() method hashes password
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data["role"],
        )

        return user
