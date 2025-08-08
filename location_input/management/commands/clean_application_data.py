import csv
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point
import requests
import io
import re
import os
from location_input.utils.command_helpers.helpers_NGED import normalise_name_and_extract_voltage_info
from location_input.utils.command_helpers.shared_helpers import get_data_csv_path, reset_csv, open_csv, clean_data_map, handle_row, report_results
from location_input.models.shared_fields import ConnectionVoltageLevel
from location_input.models.substations import Substation
from location_input.constants import VOLTAGE_CHOICES, CLEAN_CSV_HEADERS

class Command(BaseCommand):
    help = "Import and clean ngid application data from ngid website"

    def add_arguments(self, parser):
        parser.add_argument(
            'dno_group_abbr',
            type=str,
            choices=["NGED"],  # only accept NGED
            help="Only 'NGED' is currently supported."
        )
        
    def handle(self, *args, **options):
        dno_group_abbr = options['dno_group_abbr']

        clean_csv_path = get_data_csv_path("clean", dno_group_abbr)
        reset_csv(clean_csv_path, CLEAN_CSV_HEADERS, self.stdout)
        raw_csv_path = get_data_csv_path("raw", dno_group_abbr)

        with open_csv(raw_csv_path, "r") as infile, open_csv(clean_csv_path, "a") as outfile:

            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=CLEAN_CSV_HEADERS)
            
            successful_identifiers = []
            failed_identifiers = []
            
            for row in reader:
                handle_row(row, writer, dno_group_abbr, successful_identifiers, failed_identifiers, self)

        report_results(self, successful_identifiers, failed_identifiers)