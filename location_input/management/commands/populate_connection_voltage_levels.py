from django.core.management.base import BaseCommand
from location_input.models import ProposedConnectionVoltageLevel

class Command(BaseCommand):
    help = 'Populates ProposedConnectionVoltageLevel with defined voltage choices'

    def handle(self, *args, **options):
        created_count = 0
        for level, label in ProposedConnectionVoltageLevel.VOLTAGE_CHOICES:
            obj, created = ProposedConnectionVoltageLevel.objects.get_or_create(level_kv=level)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {level} kV"))
                created_count += 1
            else:
                self.stdout.write(self.style.WARNING(f"Already exists: {level} kV"))

        if created_count == 0:
            self.stdout.write(self.style.NOTICE("No new voltage levels were created."))
        else:
            self.stdout.write(self.style.SUCCESS(f"{created_count} voltage levels created."))
