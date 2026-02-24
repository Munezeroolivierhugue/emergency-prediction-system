from rest_framework.views import APIView
from rest_framework.response import Response
from incidents.models import Incident
from django.db.models import Count
from django.db.models.functions import ExtractWeekDay, ExtractHour
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

class StatisticsView(APIView):
    @extend_schema(
        summary="Get Dashboard Statistics",
        description="Retrieve aggregated incident statistics grouped by incident type and derived severity score."
    )
    def get(self, request):
        qs = Incident.objects.all()
        total_incidents = qs.count()
        critical_count = qs.filter(severity='Critical').count()
        
        TYPE_COLORS = {
            "EMS":     "#dc2626",
            "Fire":    "#ef4444",
            "Traffic": "#f97316",
        }
        
        type_qs = qs.values('type').annotate(count=Count('id'))
        by_type = []
        for item in type_qs:
            t = item['type']
            by_type.append({
                "name": t,
                "value": item['count'],
                "color": TYPE_COLORS.get(t, "#9ca3af")
            })
            
        severity_qs = qs.values('severity').annotate(count=Count('id'))
        # Ensure all core severities exist in the output dictionary
        by_severity = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for item in severity_qs:
            sev_key = item['severity'].lower()
            if sev_key in by_severity:
                by_severity[sev_key] = item['count']
            else:
                by_severity[sev_key] = item['count']

        return Response({
            "total_incidents": total_incidents,
            "critical_count": critical_count,
            "by_type": by_type,
            "by_severity": by_severity
        })

class SeverityByDayView(APIView):
    @extend_schema(summary="Get Severity by Day of Week")
    def get(self, request):
        # ExtractWeekDay returns 1 (Sunday) to 7 (Saturday)
        DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        qs = Incident.objects.values('severity') \
            .annotate(dow=ExtractWeekDay('timestamp')) \
            .values('dow', 'severity') \
            .annotate(count=Count('id'))
        
        result = {d: {"day": d, "low": 0, "medium": 0, "high": 0, "critical": 0} 
                  for d in DAY_NAMES}
                  
        for row in qs:
            if row['dow'] is not None:
                day_name = DAY_NAMES[row['dow'] - 1]  # Django: 1=Sun, 7=Sat
                sev = row['severity'].lower()
                if sev in result[day_name]:
                    result[day_name][sev] = row['count']
        
        # Return in Mon->Sun order
        ordered = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        return Response([result[d] for d in ordered])

class HourlyCallsView(APIView):
    @extend_schema(summary="Get Incident Calls by Hour (24h)")
    def get(self, request):
        qs = Incident.objects.annotate(hour=ExtractHour('timestamp')) \
            .values('hour') \
            .annotate(calls=Count('id')) \
            .order_by('hour')
        
        hour_map = {}
        for row in qs:
            if row['hour'] is not None:
                hour_map[row['hour']] = row['calls']
                
        result = [
            {"time": f"{h:02d}:00", "calls": hour_map.get(h, 0)}
            for h in range(24)
        ]
        return Response(result)