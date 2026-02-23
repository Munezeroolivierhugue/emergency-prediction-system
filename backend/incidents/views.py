from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import Incident
from .serializers import IncidentSerializer

class IncidentListView(generics.ListAPIView):
    queryset = Incident.objects.all().order_by('-timestamp')
    serializer_class = IncidentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type', 'severity', 'timestamp']