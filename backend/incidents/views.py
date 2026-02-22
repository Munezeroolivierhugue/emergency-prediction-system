<<<<<<< HEAD
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import Incident
from .serializers import IncidentSerializer

class IncidentListView(generics.ListAPIView):
    queryset = Incident.objects.all().order_by('-timestamp')
    serializer_class = IncidentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'severity']
=======
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
@permission_classes([AllowAny])  # Allow unauthenticated access for health checks
def health_check(request):
    """
    Health check endpoint for deployment monitoring.
    Returns basic system status.
    """
    return Response({
        "status": "ok",
        "service": "Emergency Severity Prediction API",
        "version": "1.0.0"
    }, status=status.HTTP_200_OK)
>>>>>>> origin/dev
