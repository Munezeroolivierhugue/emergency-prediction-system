from rest_framework import serializers

class PredictionRequestSerializer(serializers.Serializer):
    """
    Serializer for validating incoming prediction request data.
    Expected fields: type, hour, day, lat, lng.
    """
    type = serializers.CharField(max_length=100)
    hour = serializers.IntegerField(min_value=0, max_value=23)
    day = serializers.CharField(max_length=3) # e.g., 'Mon', 'Tue'
    lat = serializers.FloatField()
    lng = serializers.FloatField()

class PredictionResponseSerializer(serializers.Serializer):
    """
    Serializer for formatting outgoing prediction response data.
    Expected fields: severity, confidence.
    """
    severity = serializers.CharField(max_length=20) # e.g., 'Low', 'Medium', 'High', 'Critical'
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
