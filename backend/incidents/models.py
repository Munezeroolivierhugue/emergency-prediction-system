from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Location(models.Model):
    """Model for storing location information"""
    district = models.CharField(max_length=100)
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    address = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'locations'
        indexes = [
            models.Index(fields=['district']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.district} ({self.latitude}, {self.longitude})"


class Incident(models.Model):
    """Model for storing emergency incidents"""
    
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    INCIDENT_TYPES = [
        ('FIRE', 'Fire'),
        ('MEDICAL', 'Medical Emergency'),
        ('ACCIDENT', 'Traffic Accident'),
        ('CRIME', 'Crime'),
        ('NATURAL_DISASTER', 'Natural Disaster'),
        ('HAZMAT', 'Hazardous Materials'),
        ('RESCUE', 'Rescue Operation'),
        ('OTHER', 'Other'),
    ]
    
    incident_type = models.CharField(max_length=50, choices=INCIDENT_TYPES)
    description = models.TextField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='incidents')
    timestamp = models.DateTimeField(auto_now_add=True)
    actual_severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        blank=True,
        null=True
    )
    reported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reported_incidents'
    )
    response_time_minutes = models.IntegerField(
        null=True,
        blank=True,
        help_text="Time taken to respond in minutes"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'incidents'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['incident_type']),
            models.Index(fields=['actual_severity']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.incident_type} - {self.location.district} ({self.timestamp})"


class Prediction(models.Model):
    """Model for storing ML predictions"""
    
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    incident = models.OneToOneField(
        Incident,
        on_delete=models.CASCADE,
        related_name='prediction'
    )
    predicted_severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Confidence score between 0 and 1"
    )
    model_version = models.CharField(max_length=50, default='v1.0')
    prediction_time = models.DateTimeField(auto_now_add=True)
    
    # Store probability distribution for all classes
    probability_low = models.FloatField(default=0.0)
    probability_medium = models.FloatField(default=0.0)
    probability_high = models.FloatField(default=0.0)
    probability_critical = models.FloatField(default=0.0)
    
    class Meta:
        db_table = 'predictions'
        ordering = ['-prediction_time']
        indexes = [
            models.Index(fields=['predicted_severity']),
            models.Index(fields=['-prediction_time']),
        ]
    
    def __str__(self):
        return f"Prediction for Incident #{self.incident.id}: {self.predicted_severity} ({self.confidence_score:.2%})"


class ResponseResource(models.Model):
    """Model for recommended response resources"""
    
    severity_level = models.CharField(max_length=20)
    resource_type = models.CharField(max_length=100)
    quantity = models.IntegerField()
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'response_resources'
    
    def __str__(self):
        return f"{self.severity_level}: {self.quantity}x {self.resource_type}"