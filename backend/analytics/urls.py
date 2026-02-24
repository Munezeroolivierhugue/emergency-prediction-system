from django.urls import path
from .views import StatisticsView, SeverityByDayView, HourlyCallsView

urlpatterns = [
    path('statistics/', StatisticsView.as_view(), name='statistics'),
    path('severity-by-day/', SeverityByDayView.as_view(), name='severity-by-day'),
    path('hourly/', HourlyCallsView.as_view(), name='hourly'),
]