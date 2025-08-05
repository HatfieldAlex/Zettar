from django.core.management.base import BaseCommand
from location_input.models import (
    ConnectionStatus,
)  # adjust import to your actual app


class Command(BaseCommand):
    help = "Populate the ConnectionStatus table with defined status choices"

    def handle(self, *args, **options):
        created_count = 0
        for code, label in ConnectionStatus.STATUS_CHOICES:
            obj, created = ConnectionStatus.objects.get_or_create(status=code)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created: {code} - {label}")
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f"Already exists: {code} - {label}")
                )

        if created_count == 0:
            self.stdout.write(
                self.style.NOTICE("No new statuses were created.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"{created_count} status entries created.")
            )
