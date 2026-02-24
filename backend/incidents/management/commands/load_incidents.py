from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Load incidents from CSV file'

    def handle(self, *args, **kwargs):
        self.stdout.write('load_incidents command - to be implemented by CARD-16')