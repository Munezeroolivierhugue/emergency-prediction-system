from django.urls import path
from .views import PredictSeverityView

urlpatterns = [
    path('predict/', PredictSeverityView.as_view(), name='predict-severity'),
]