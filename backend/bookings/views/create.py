from accounts.permissions import IsAttendee
from bookings.serializers import BookingSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class BookingCreateView(APIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsAttendee]

    def post(self, request):
        serializer = BookingSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            booking = serializer.save()
            return Response({"booking_id": booking.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
