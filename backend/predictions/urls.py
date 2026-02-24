from django.urls import path
from .views import PredictSeverityView, IncidentListView, IncidentUpdateView

urlpatterns = [
    path('predict/', PredictSeverityView.as_view(), name='predict-severity'),
    path('incidents/', IncidentListView.as_view(), name='incident-list'),
    path('incidents/<str:pk>/', IncidentUpdateView.as_view(), name='incident-update'),
]