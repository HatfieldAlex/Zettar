import ast
import csv
import io
import re
from datetime import date
from pathlib import Path

import requests
from django.contrib.gis.geos import GEOSGeometry, Point
from django.core.management.base import BaseCommand, CommandError

from location_input.models import *
from location_input.state import integrated_dno_groups
from location_input.utils.command_helpers import *


class Command(BaseCommand):
    help = "Process cleaned grid application data - requires DNO group variable input"

    def add_arguments(self, parser):
        parser.add_argument(
            'dno_group_abbr',
            type=str,
            choices=integrated_dno_groups,
            help=f"Only DNOs of {', '.join(integrated_dno_groups)} is currently supported."
        )      

    def handle(self, *args, **options):
        dno_group_abbr = options['dno_group_abbr']
        cleaned_application_data_csv_path = get_data_csv_path("clean", "connection_applications", dno_group_abbr)
        clear_existing_cleaned_data(self.stdout, "application", dno_group_abbr)

        with open_csv(cleaned_application_data_csv_path, "r") as file:
            reader = csv.DictReader(file)

            successful_identifiers = []
            failed_identifiers = []

            for row in reader:
                handle_row_process_application(self.style, row, dno_group_abbr, successful_identifiers, failed_identifiers, self.stdout, self.stderr)

        report_results(self, successful_identifiers, failed_identifiers)
