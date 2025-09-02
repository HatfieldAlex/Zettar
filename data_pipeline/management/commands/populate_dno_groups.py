from django.core.management.base import BaseCommand
from core.models import DNOGroup


class Command(BaseCommand):
    help = "Populates the DNOGroup table with predefined DNO entries"

    def handle(self, *args, **options):
        groups = [
            ("ukpn", "UK Power Networks"),
            ("nged", "National Grid Electricity Distribution"),
            ("spen", "SP Energy Networks"),
            ("np", "Northern Powergrid"),
            ("enw", "Electricity North West"),
            ("ssen", "Scottish and Southern Electricity Networks"),
        ]

        created_count = 0
        for (
            abbr,
            _,
        ) in groups:  
            obj, created = DNOGroup.objects.get_or_create(
                abbr=abbr, defaults={}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {abbr}"))
                created_count += 1
            else:
                self.stdout.write(f"Exists: {abbr}")

        self.stdout.write(
            self.style.SUCCESS(f"Done. {created_count} new DNOGroup(s) added.")
        )
