from rest_framework import serializers

class PredictionRequestSerializer(serializers.Serializer):
    """
    Serializer for validating incoming prediction request data.
    Expected fields: type, hour, day, lat, lng, month, day_of_week.
    """
    type = serializers.CharField(max_length=100)
    hour = serializers.IntegerField(min_value=0, max_value=23)
    day = serializers.CharField(max_length=3, required=False) # e.g., 'Mon', 'Tue'
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    month = serializers.IntegerField(min_value=1, max_value=12, default=1)
    day_of_week = serializers.IntegerField(min_value=0, max_value=6, default=0)

class PredictionResponseSerializer(serializers.Serializer):
    """
    Serializer for formatting outgoing prediction response data.
    Expected fields: severity, confidence, recommended_response.
    """
    severity = serializers.CharField(max_length=20) # e.g., 'Low', 'Medium', 'High', 'Critical'
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    recommended_response = serializers.CharField(max_length=100)
