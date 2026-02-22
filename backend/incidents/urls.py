<<<<<<< HEAD
from django.urls import path
from .views import IncidentListView

urlpatterns = [
    path('', IncidentListView.as_view(), name='incident-list'),
=======
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import health_check

# Create a router for viewsets (if you add them later)
router = DefaultRouter()

urlpatterns = [
    # Health check endpoints
    path('health/', health_check, name='health-check'),
    
    path('', include(router.urls)),
    
>>>>>>> origin/dev
]