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