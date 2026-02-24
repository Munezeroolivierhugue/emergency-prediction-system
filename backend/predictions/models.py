from django.db import models
import uuid

class Incident(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Dispatched', 'Dispatched'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    id = models.CharField(max_length=20, primary_key=True, editable=False)
    incident_type = models.CharField(max_length=100)
    location = models.CharField(max_length=255, null=True, blank=True)
    lat = models.FloatField()
    lng = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(max_length=20)
    confidence = models.CharField(max_length=10, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def save(self, *args, **kwargs):
        if not self.id:
            # Generate ID like INC-1001
            last_incident = Incident.objects.all().order_by('time').last()
            if not last_incident or not last_incident.id.startswith('INC-'):
                new_int = 1001
            else:
                try:
                    last_int = int(last_incident.id.split('-')[1])
                    new_int = last_int + 1
                except ValueError:
                    new_int = 1001
            self.id = f"INC-{new_int}"
        super(Incident, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.id} - {self.incident_type} at {self.location or 'Unknown Location'}"
