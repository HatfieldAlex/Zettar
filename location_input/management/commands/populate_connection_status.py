from django.core.management.base import BaseCommand
from django.db import transaction
from location_input.models import ConnectionStatus


class Command(BaseCommand):
    help = "Populate ConnectionStatus with the defined STATUS_CHOICES."

    def handle(self, *args, **options):
        created_count = 0

        with transaction.atomic():
            for value, _label in ConnectionStatus.STATUS_CHOICES:
                obj, created = ConnectionStatus.objects.get_or_create(status=value)
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created: {value}"))
                    created_count += 1
                else:
                    self.stdout.write(self.style.WARNING(f"Already exists: {value}"))

        if created_count == 0:
            self.stdout.write("No new statuses were created.")
        else:
            self.stdout.write(self.style.SUCCESS(f"{created_count} statuses created."))
