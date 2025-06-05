from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .constants import (
    PASSWORD_RESET_MESSAGE,
    AccountsMessages,
    PasswordMessasges,
)
from .serializers import (
    ChangePasswordSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Handle user creation."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API view for retrieving and updating the authenticated user's profile.
    Requires authentication.
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Returns the authenticated user instance.
        """
        return self.request.user


class ChangePasswordView(APIView):
    """
    API view for an authenticated user to change their password.
    Requires authentication.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid(raise_exception=True):
            # Passed all validations
            # Call custom save() method of serializer
            serializer.save()
            return Response(
                {"detail": "Password updated successfully."}, status=status.HTTP_200_OK
            )

        # Didn't pass validation
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    API view to request a password reset email.
    """

    # Allow unauthenticated users to request reset
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            # Always return a success message for security (prevents email enumeration)
            return Response(
                {"detail": PASSWORD_RESET_MESSAGE},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    API view to confirm a password reset with UID and token.
    """

    # Allow unauthenticated users to confirm reset
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"detail": PasswordMessasges.RESET_CONFIRM}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeactivateView(APIView):
    """
    API view for an authenticated user to deactivate their own account (soft delete).
    Sets is_active to False.
    """

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user
        if not user.is_active:
            return Response(
                {"detail": AccountsMessages.ALREADY_INACTIVE},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.is_active = False
        user.save()

        return Response(
            {"detail": AccountsMessages.DEACTIVATED},
            status=status.HTTP_204_NO_CONTENT,
        )
