from django.contrib import admin
from .models import Incident

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['type', 'severity', 'timestamp', 'latitude', 'longitude']
    list_filter = ['type', 'severity']
    search_fields = ['description']
    date_hierarchy = 'timestamp'