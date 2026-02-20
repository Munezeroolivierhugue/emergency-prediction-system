"""
Management command to load incident data from CSV file into the database.
CARD-16: Database Setup and Data Loading
"""
import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from incidents.models import Location, Incident


class Command(BaseCommand):
    help = 'Load incident data from CSV file into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='../data/processed/incidents_cleaned.csv',
            help='Path to the CSV file (default: ../data/processed/incidents_cleaned.csv)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading'
        )

    def handle(self, *args, **options):
        csv_file = options['file']
        clear_data = options['clear']

        # Resolve the file path relative to manage.py location
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        csv_path = os.path.join(base_dir, csv_file)

        # Check if file exists
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_path}'))
            return

        # Clear existing data if requested
        if clear_data:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Incident.objects.all().delete()
            Location.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        # Load data
        self.stdout.write(self.style.SUCCESS(f'Loading data from: {csv_path}'))
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                loaded_count = 0
                skipped_count = 0
                location_cache = {}  # Cache locations to avoid duplicates
                
                incidents_to_create = []
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    try:
                        # Extract data from CSV
                        lat = float(row['lat'])
                        lng = float(row['lng'])
                        incident_type = row['type'].upper()
                        subtype = row['subtype']
                        severity = row['severity'].upper()
                        timestamp_str = row['timestamp']
                        district = row.get('district', 'UNKNOWN')
                        
                        # Parse timestamp
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        
                        # Map CSV type to model INCIDENT_TYPES
                        type_mapping = {
                            'EMS': 'MEDICAL',
                            'FIRE': 'FIRE',
                            'TRAFFIC': 'ACCIDENT',
                        }
                        mapped_type = type_mapping.get(incident_type, 'OTHER')
                        
                        # Get or create location (use cache to avoid duplicate queries)
                        location_key = f"{district}_{lat}_{lng}"
                        if location_key not in location_cache:
                            location, created = Location.objects.get_or_create(
                                district=district,
                                latitude=lat,
                                longitude=lng,
                                defaults={'address': f'{district} area'}
                            )
                            location_cache[location_key] = location
                        else:
                            location = location_cache[location_key]
                        
                        # Create incident object (don't save yet for bulk insert)
                        incident = Incident(
                            incident_type=mapped_type,
                            description=f"{incident_type}: {subtype}",
                            location=location,
                            timestamp=timestamp,
                            actual_severity=severity,
                            is_active=False  # Historical data
                        )
                        incidents_to_create.append(incident)
                        loaded_count += 1
                        
                        # Bulk insert every 100 records for efficiency
                        if len(incidents_to_create) >= 100:
                            Incident.objects.bulk_create(incidents_to_create)
                            self.stdout.write(f'Processed {loaded_count} incidents...')
                            incidents_to_create = []
                        
                    except (ValueError, KeyError) as e:
                        skipped_count += 1
                        self.stdout.write(
                            self.style.WARNING(f'Skipping row {row_num}: {str(e)}')
                        )
                        continue
                
                # Insert remaining incidents
                if incidents_to_create:
                    Incident.objects.bulk_create(incidents_to_create)
                
                # Summary
                self.stdout.write(self.style.SUCCESS('=' * 50))
                self.stdout.write(self.style.SUCCESS(f'✓ Successfully loaded {loaded_count} incidents'))
                if skipped_count > 0:
                    self.stdout.write(self.style.WARNING(f'⚠ Skipped {skipped_count} invalid rows'))
                self.stdout.write(self.style.SUCCESS(f'✓ Created {len(location_cache)} unique locations'))
                self.stdout.write(self.style.SUCCESS('=' * 50))
                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {csv_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading data: {str(e)}'))
