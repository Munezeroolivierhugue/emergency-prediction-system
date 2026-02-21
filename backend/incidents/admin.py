from django.contrib import admin
from .models import Location, Incident, Prediction, ResponseResource


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['district', 'latitude', 'longitude']
    search_fields = ['district']


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['incident_type', 'actual_severity', 'timestamp', 'location', 'is_active']
    list_filter = ['incident_type', 'actual_severity', 'is_active']
    search_fields = ['description']
    date_hierarchy = 'timestamp'


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['incident', 'predicted_severity', 'confidence_score', 'prediction_time']
    list_filter = ['predicted_severity']


@admin.register(ResponseResource)
class ResponseResourceAdmin(admin.ModelAdmin):
    list_display = ['severity_level', 'resource_type', 'quantity']
    list_filter = ['severity_level']
