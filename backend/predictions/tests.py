from unittest.mock import patch
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class PredictSeverityViewTests(APITestCase):
    """
    Tests for the PredictSeverityView API endpoint.
    """

    def setUp(self):
        """
        Set up the test environment.
        This includes creating a test user and authenticating the client.
        """
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpassword123'
        )
        self.client.force_authenticate(user=self.user)
        self.predict_url = reverse('predict-severity')
        self.valid_payload = {
            "type": "Fire",
            "hour": 14,
            "day": "Mon",
            "lat": 40.1,
            "lng": -75.3
        }

    @patch('predictions.ml_service.MLService.predict_severity')
    def test_predict_severity_success(self, mock_predict):
        """
        Test a successful prediction request.
        """
        # Configure the mock to return a sample prediction
        mock_response = {"severity": "High", "confidence": 0.85}
        mock_predict.return_value = mock_response

        # Make the API request
        response = self.client.post(self.predict_url, self.valid_payload, format='json')

        # Assert the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, mock_response)
        
        # Verify that the service was called with the validated data
        mock_predict.assert_called_once_with(self.valid_payload)

    def test_predict_severity_unauthenticated(self):
        """
        Test that an unauthenticated request is rejected.
        """
        # Clear authentication for this test
        self.client.force_authenticate(user=None)
        
        response = self.client.post(self.predict_url, self.valid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_predict_severity_invalid_payload(self):
        """
        Test that a request with an invalid payload is rejected.
        """
        invalid_payload = self.valid_payload.copy()
        del invalid_payload['type']  # Missing required 'type' field
        
        response = self.client.post(self.predict_url, invalid_payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('type', response.data) # Check that the error message mentions the 'type' field

    @patch('predictions.ml_service.MLService.predict_severity')
    def test_predict_severity_model_not_found(self, mock_predict):
        """
        Test that the API handles a FileNotFoundError gracefully.
        """
        # Configure the mock to raise a FileNotFoundError
        mock_predict.side_effect = FileNotFoundError("Model file not found at path")

        response = self.client.post(self.predict_url, self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("ML model not found", response.data['error'])

    @patch('predictions.ml_service.MLService.predict_severity')
    def test_predict_severity_internal_error(self, mock_predict):
        """
        Test that the API handles a generic server error during prediction.
        """
        # Configure the mock to raise a generic Exception
        mock_predict.side_effect = Exception("An unexpected error occurred")

        response = self.client.post(self.predict_url, self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("An unexpected error occurred", response.data['error'])
