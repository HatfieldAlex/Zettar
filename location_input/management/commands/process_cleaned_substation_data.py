import csv
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point
import requests
import io
import re
from location_input.utils.command_helpers.shared_helpers import get_data_csv_path, reset_csv, open_csv, clean_data_map, handle_row, report_results
from location_input.models.shared_fields import ConnectionVoltageLevel
import ast
from django.contrib.gis.geos import GEOSGeometry
from location_input.models.substations import DNOGroup, Substation
from location_input.constants import VOLTAGE_CHOICES, CLEAN_SUBSTATION_CSV_HEADERS
from location_input.utils.command_helpers.process.shared_helpers_process import process_row, handle_row_process_substation
from location_input.utils.command_helpers.process.shared_helpers_process import clear_existing_cleaned_data


class Command(BaseCommand):
    help = "Process cleaned substation data"

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


