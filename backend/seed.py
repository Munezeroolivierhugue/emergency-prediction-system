import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emergency_system.settings')
django.setup()

from incidents.models import Incident

def seed_incidents():
    print("Clearing old incidents...")
    Incident.objects.all().delete()
    
    types = ['EMS', 'EMS', 'EMS', 'Fire', 'Traffic', 'Traffic']
    severities = ['Low', 'Low', 'Low', 'Medium', 'Medium', 'High', 'Critical']
    statuses = ['Active', 'Resolved', 'Resolved', 'Resolved']
    locations = [
        "Main St & 5th Ave", "Route 202 N", "Oak Rd", "Cedar Ln", 
        "Highland Blvd", "Downtown Plaza", "Highway 95", "Industrial Park"
    ]
    
    now = timezone.now()
    incidents_to_create = []
    
    print("Generating 100 random incidents over the last 7 days...")
    for _ in range(100):
        # Random time within the last 7 days
        days_ago = random.randint(0, 6)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        incident_time = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        
        inc = Incident(
            type=random.choice(types),
            severity=random.choice(severities),
            latitude=round(random.uniform(39.0, 41.0), 4),
            longitude=round(random.uniform(-76.0, -74.0), 4),
            location=random.choice(locations),
            timestamp=incident_time,
            description=f"Generated mock incident summary for testing.",
            status=random.choice(statuses),
            confidence=round(random.uniform(0.65, 0.99), 2)
        )
        incidents_to_create.append(inc)
        
    Incident.objects.bulk_create(incidents_to_create)
    print(f"Successfully created {len(incidents_to_create)} incidents!")

if __name__ == '__main__':
    seed_incidents()
