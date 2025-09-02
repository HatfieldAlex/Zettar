from django.core.management.base import BaseCommand
from core.models import DNOGroup


class Command(BaseCommand):
    help = "Populates the DNOGroup table with predefined DNO entries"

    def handle(self, *args, **options):
        groups = ["ukpn", "nged", "spen", "np", "enw", "ssen"]

        created_count = 0
        for abbr in groups:  
            obj, created = DNOGroup.objects.get_or_create(abbr=abbr, defaults={})

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {abbr}"))
                created_count += 1
            else:
                self.stdout.write(f"Exists: {abbr}")

        self.stdout.write(
            self.style.SUCCESS(f"Complete. {created_count} new DNOGroup(s) populated.")
        )
