from django.urls import path
from .views import PredictSeverityView
from incidents.views import IncidentListView

urlpatterns = [
    path('predict/', PredictSeverityView.as_view(), name='predict-severity'),
    path('incidents/', IncidentListView.as_view(), name='incident-list'),
]