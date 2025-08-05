from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
from location_input.models.new_connections import ReportingPeriod


class Command(BaseCommand):
    help = "Add a ReportingPeriod with start and end dates"

    def add_arguments(self, parser):
        parser.add_argument(
            "start_date", type=str, help="Start date in YYYY-MM-DD format"
        )
        parser.add_argument("end_date", type=str, help="End date in YYYY-MM-DD format")

    def handle(self, *args, **options):
        start_date_str = options["start_date"]
        end_date_str = options["end_date"]

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError as e:
            raise CommandError(f"Invalid date format: {e}. Use YYYY-MM-DD.")

        reporting_period, created = ReportingPeriod.objects.get_or_create(
            start_date=start_date, end_date=end_date
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created ReportingPeriod for {start_date} to {end_date}."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"ReportingPeriod already exists for {start_date} to {end_date}."
                )
            )
