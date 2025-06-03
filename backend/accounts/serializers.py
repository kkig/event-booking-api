from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
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


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change requests.
    Requires old_password, new_password1, and new_password2 (confirmation).
    """

    old_password = serializers.CharField(required=True, write_only=True)
    new_password1 = serializers.CharField(required=True, write_only=True)
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        """
        Field-level validate_<field_name> method
        """
        # Called with the specific value of <field_name>.
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                "Your old password was entered incorrectly. Please try again."
            )
        return value

    def validate(self, data):
        """
        Serializer-level method. Perform cross-field validation.
        """
        # Called after field-level validation passed.
        # data is dictionary containing all the validated values for all fields.

        # Validate that new_password1 and new_password2 match
        if data["new_password1"] != data["new_password2"]:
            raise serializers.ValidationError(
                {"new_password2": "New passwords do not match."}
            )

        # Apply Django's password validators to the new password
        try:
            validate_password(data["new_password1"], self.context["request"].user)
        except DjangoValidationError as e:  # Catch Django's ValidationError
            # Mat Django's validation errors to the 'new_password1' field
            raise serializers.ValidationError({"new_password1": list(e.messages)})
        except Exception as e:
            # Catch any other unexpected errors during password validation
            raise serializers.ValidationError(
                {"new_password1": f"An unexpected error occurred: {e}"}
            )

        return data

    def save(self, **kwargs):
        """
        Custom save method to set the new password for the user.
        Called after validation. (is_valid() is `True`).
        """
        # self.validation_data will be populated if validate() succeeded.
        user = self.context["request"].user

        # Explicitly assert that validation_data is a dictionary.
        assert isinstance(
            self.validated_data, dict
        ), "Validated data should be a dictionary at this point."

        # At this point, Pylane understands self.validated_data is a dict.
        user.set_password(self.validated_data["new_password1"])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset email.
    Takes email and validates its existence.
    """

    email = serializers.EmailField(required=True)

    class Meta:
        fields = ["email"]

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            # Store the user object in serializer context for later user in save()
            self.context["user"] = user
        except User.DoesNotExist:
            # For security reasons, don't confirm if email exists or not.
            # Just return a success message even if email doesn't exist.
            # This prevents email enumeration.
            pass
        return value

    def save(self):
        """
        Generates a password reset token and sends an email to the user.
        """
        user = self.context.get("user")
        if user:
            # Only send email if user exists (after validation)
            token_generator = PasswordResetTokenGenerator()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)

            # Construct the reset link (Frontend needs to handle this base URL)
            # For testing, you might need a placeholder or a mock URL.
            # In a real app, this would be a link to your frontend's password reset page
            # e.g., f"https://example.com/reset-password/{uid}/{token}/"

            # Placeholder URL
            reset_link = f"http://127.0.0.1:8000/api/auth/password-reset-confirmation/{uid}/{token}/"

            # Render email content (you'll create this template)
            email_subject = "Password Reset Request"
            email_body = render_to_string(
                "accounts/password_reset_email.html",
                {
                    "user": user,
                    "reset_link": reset_link,
                    "domain": "127.0.0.1:8000",
                    "uid": uid,
                    "token": token,
                },
            )

            email = EmailMessage(
                email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [user.email]
            )
            email.send()

        # Always returns success to prevent email enumeration, even if user doesn't exist
        return True
