import ast
import csv
import io
import re
from pathlib import Path

import requests
from django.contrib.gis.geos import GEOSGeometry, Point
from django.core.management.base import BaseCommand, CommandError

from location_input.constants import VOLTAGE_CHOICES, CLEAN_SUBSTATION_CSV_HEADERS
from location_input.models import *
from location_input.state import integrated_dno_groups
from location_input.utils.command_helpers import *

class Command(BaseCommand):
    help = "Process cleaned substation data"

    def add_arguments(self, parser):
        parser.add_argument(
            'dno_group_abbr',
            type=str,
            choices=integrated_dno_groups,
            help=f"Only DNOs of {', '.join(integrated_dno_groups)} is currently supported."
        )  

    def add_arguments(self, parser):
        parser.add_argument('dno_group_abbr', type=str)

    def handle(self, *args, **options):
        dno_group_abbr = options['dno_group_abbr']
        clear_existing_cleaned_data(self.stdout, 'substation', dno_group_abbr)
        clean_csv_path = get_data_csv_path("clean", "substation_locations", dno_group_abbr)

        with open_csv(clean_csv_path, "r") as file:
            reader = csv.DictReader(file)

            successful_identifiers = []
            failed_identifiers = []

            for row in reader:
                handle_row_process_substation(row, successful_identifiers, failed_identifiers, self, dno_group_abbr)

        report_results(self, successful_identifiers, failed_identifiers)


