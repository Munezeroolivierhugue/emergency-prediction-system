from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .serializers import PredictionRequestSerializer, PredictionResponseSerializer
from .ml_service import MLService

class PredictSeverityView(APIView):
    """
    API endpoint to predict the severity of an emergency incident.
    Requires authentication.
    """
    permission_classes = [AllowAny] # Allow public access

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to predict incident severity.
        """
        serializer = PredictionRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                prediction_data = MLService.predict_severity(serializer.validated_data)
                response_serializer = PredictionResponseSerializer(data=prediction_data)
                response_serializer.is_valid(raise_exception=True) # Validate the output as well

                return Response(response_serializer.data, status=status.HTTP_200_OK)
            except FileNotFoundError as e:
                return Response(
                    {"error": f"ML model not found: {e}"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            except IOError as e:
                return Response(
                    {"error": f"Error loading or using ML model: {e}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except Exception as e:
                # Catch any other unexpected errors during prediction
                return Response(
                    {"error": f"An unexpected error occurred during prediction: {e}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
