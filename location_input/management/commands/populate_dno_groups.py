from django.core.management.base import BaseCommand
from location_input.models.substations import DNOGroup


class Command(BaseCommand):
    help = "Populates the DNOGroup table with predefined DNO entries"

    def handle(self, *args, **options):
        groups = [
            ('UKPN', 'UK Power Networks'),
            ('NGED', 'National Grid Electricity Distribution'),
            ('SPEN', 'SP Energy Networks'),
            ('NP', 'Northern Powergrid'),
            ('ENW', 'Electricity North West'),
            ('SSEN', 'Scottish and Southern Electricity Networks'),
        ]

        created_count = 0
        for abbr, _ in groups:  # Ignoring name for now since the model only has 'abbr'
            obj, created = DNOGroup.objects.get_or_create(
                abbr=abbr,
                defaults={}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {abbr}"))
                created_count += 1
            else:
                self.stdout.write(f"Exists: {abbr}")

        self.stdout.write(self.style.SUCCESS(f"Done. {created_count} new DNOGroup(s) added."))
