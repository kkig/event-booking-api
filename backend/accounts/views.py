from rest_framework import generics

from .models import User
from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    """Handle user creation."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
