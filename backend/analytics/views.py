from rest_framework.views import APIView
from rest_framework.response import Response
from incidents.models import Incident
from django.db.models import Count

class StatisticsView(APIView):
    def get(self, request):
        by_type = dict(
            Incident.objects.values_list('type')
                            .annotate(count=Count('id'))
                            .values_list('type', 'count')
        )
        by_severity = dict(
            Incident.objects.values_list('severity')
                            .annotate(count=Count('id'))
                            .values_list('severity', 'count')
        )
        return Response({
            "by_type": by_type,
            "by_severity": by_severity
        })