from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Defines serializer for user registration.
    `ModelSerializer` will adds validators based on model field constrains.
    """

    # Overrides password to validate and write-only
    # Exclude from response
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        # Model to base serialization on
        model = User
        # Fields to include in I/O JSON
        fields = ("username", "email", "password", "role")

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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # DO NOT include 'password
        # Use a separate password change endpoint.
        fields = ["id", "username", "email", "role"]

        # User usually can't change their ID or role
        read_only_fields = ["id", "role"]

    def validate_email(self, value):
        if self.instance and self.instance.email == value:
            # Email hasn't changed for this instance
            return value

        # Check if the email already exists for any other user
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "This email address is already in use by another user."
            )
        return value
