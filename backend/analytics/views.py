from rest_framework.views import APIView
from rest_framework.response import Response
from incidents.models import Incident
from django.db.models import Count
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

class StatisticsView(APIView):
    @extend_schema(
        summary="Get Dashboard Statistics",
        description="Retrieve aggregated incident statistics grouped by incident type and derived severity score.",
        responses={
            200: inline_serializer(
                name='StatisticsResponse',
                fields={
                    'by_type': serializers.DictField(child=serializers.IntegerField()),
                    'by_severity': serializers.DictField(child=serializers.IntegerField()),
                }
            )
        }
    )
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