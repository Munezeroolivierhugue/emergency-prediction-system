from django.db import models
from django.utils import timezone


class Incident(models.Model):
    SEVERITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]

    TYPE_CHOICES = [
        ('EMS', 'EMS'),
        ('Fire', 'Fire'),
        ('Traffic', 'Traffic'),
    ]

    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    latitude = models.FloatField()
    longitude = models.FloatField()
    location = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    confidence = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Active')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.severity} at {self.timestamp}"