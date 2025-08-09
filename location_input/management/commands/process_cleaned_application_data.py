import csv
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point
import requests
import io
import re
from location_input.utils.command_helpers.application_data.helpers_application_NGED import normalise_name_and_extract_voltage_info
from location_input.models.shared_fields import ConnectionVoltageLevel
from location_input.utils.command_helpers.shared_helpers import get_data_csv_path, reset_csv, open_csv, clean_data_map, handle_row, report_results
import ast
from django.contrib.gis.geos import GEOSGeometry
from datetime import date
from location_input.models.new_connections import (
    NewConnection,
    ConnectionStatus,
    ReportingPeriod,
)
from location_input.models.substations import DNOGroup, Substation
from location_input.utils.command_helpers.process.helpers_NGED import clear_existing_cleaned_application_data_NGED, process_row_application_NGED, handle_row_process_application_NGED
from location_input.utils.command_helpers.process.shared_helpers_process import clear_existing_cleaned_data
from location_input.utils.command_helpers.process.shared_helpers_process import handle_row_process_application

class Command(BaseCommand):
    help = "Process cleaned grid application data - requires DNO group variable input"

    def add_arguments(self, parser):
        parser.add_argument('dno_group_abbr', type=str)

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
