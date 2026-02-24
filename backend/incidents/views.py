from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import Incident
from .serializers import IncidentSerializer

from drf_spectacular.utils import extend_schema

@extend_schema(
    summary="List Historical Incidents",
    description="Retrieve a paginated list of all stored emergency incidents, ordered by the most recent timestamp. Includes filtering options."
)
class IncidentListView(generics.ListAPIView):
    queryset = Incident.objects.all().order_by('-timestamp')
    serializer_class = IncidentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'severity', 'timestamp']