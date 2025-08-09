import csv
import io
import os
import re
from pathlib import Path

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand, CommandError
import requests

from location_input.constants import VOLTAGE_CHOICES, CLEAN_APPLICATION_CSV_HEADERS
from location_input.models import Substation, ConnectionVoltageLevel
from location_input.state import integrated_dno_groups
from location_input.utils.command_helpers import *

class Command(BaseCommand):
    help = "Import and clean application data"

    def add_arguments(self, parser):
        parser.add_argument(
            'dno_group_abbr',
            type=str,
            choices=integrated_dno_groups,
            help=f"Only DNOs of {', '.join(integrated_dno_groups)} is currently supported."
        )      
        
    def handle(self, *args, **options):
        dno_group_abbr = options['dno_group_abbr']

        clean_csv_path = get_data_csv_path("clean", "connection_applications", dno_group_abbr)
        reset_csv(clean_csv_path, CLEAN_APPLICATION_CSV_HEADERS, self.stdout)
        raw_csv_path = get_data_csv_path("raw", "connection_applications", dno_group_abbr)

        with open_csv(raw_csv_path, "r") as infile, open_csv(clean_csv_path, "a") as outfile:

            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=CLEAN_APPLICATION_CSV_HEADERS)
            
            successful_identifiers = []
            failed_identifiers = []
            
            for row in reader:
                handle_row(row, writer, dno_group_abbr, "application", successful_identifiers, failed_identifiers, self)

        report_results(self, successful_identifiers, failed_identifiers)