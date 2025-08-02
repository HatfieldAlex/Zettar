import csv 
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point 
import requests
import io
import re
import os
from location_input.utils.command_helpers import normalise_name_and_extract_voltage_info
from location_input.models.shared_fields import ConnectionVoltageLevel 
from location_input.models.substations import (
    DNOGroup,
    GSPSubstation,
    BSPSubstation,
    PrimarySubstation,
)

class Command(BaseCommand):
    help = 'Import and clean ngid data from ngid website'

    def handle(self, *args, **options):

        clean_csv_path = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'ngid' / 'clean' / 'ngid_substations_locations_clean.csv'

        self.clear_existing_nged_substations_data(clean_csv_path)
        self.initialise_blank_csv(clean_csv_path)

        raw_csv_path = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'ngid' / 'raw' / 'ngid_substation_locations_raw.csv'

        success_ids = []
        failure_ids = []

        with open(raw_csv_path, 'r', encoding='utf-8') as infile, \
        open(clean_csv_path, 'a', encoding='utf-8', newline='') as outfile:

            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=['name', 'type', 'geolocation', 'dno', '6.6', '11', '33', '66', '132'])

            for row in reader:
                if row['Substation Type'] in {'132kv Switching Station', 'Ehv Switching Station'}:
                    continue
                substation_number = row.get('Substation Number')
                try:
                    cleaned_row = self.clean_row(row)
                    writer.writerow(cleaned_row)           
                    self.stdout.write(self.style.SUCCESS(f"Successfully cleaned row with substationID {substation_number}"))
                    success_ids.append(substation_number)
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error cleaning row of substationID: {substation_number}"))
                    self.stderr.write(self.style.ERROR(str(e)))
                    failure_ids.append(substation_number)

        self.stdout.write(self.style.SUCCESS(
            f"raw CSV clean complete: {len(success_ids)} succeeded, {len(failure_ids)} failed."
        ))

        if failure_ids:
            failed_list = ', '.join(failure_ids)
            self.stderr.write(self.style.ERROR(f"Failed substationIDs: {failed_list}"))


    def clear_existing_nged_substations_data(self, PATH):
        if PATH.exists():
            self.stdout.write("Removing previous cleaned NGED substation data csv...")
            PATH.unlink()
            self.stdout.write("...cleaned NGED substation data csv removed.")

    def initialise_blank_csv(self, PATH):
        self.stdout.write(f"Creating blank CSV...")
        os.makedirs(os.path.dirname(PATH), exist_ok=True)
        
        voltage_levels = [6.6, 11, 33, 66, 132]
        headers = ['name', 'type', 'geolocation', 'dno', '6.6', '11', '33', '66', '132']
        with open(PATH, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
        self.stdout.write(f"Cleaned CSV initialised: {PATH.name}")


    def clean_row(self, row):
        ss_type = row['Substation Type']
        ss_name = row['Substation Name']
        ss_lat = row['Latitude']
        ss_lng = row['Longitude']

        type_map = {
            'Primary Substation': 'primary',
            'Bulk Supply Point': 'bsp',
            'Super Grid Substation': 'gsp',
        }


        ss_dno = 'NGED'
        ss_geolocation = Point(float(ss_lat), float(ss_lng))
        ss_name, ss_voltages = self.normalise_name_and_extract_voltage_info(row['Substation Name'])
        ss_type = type_map[ss_type]

        cleaned_row = {
            'name': ss_name,
            'type': ss_type,
            'geolocation': ss_geolocation.wkt,
            'dno': ss_dno,
        } | ss_voltages

        return cleaned_row


    def normalise_name_and_extract_voltage_info(self, ss_name):

        #remove basic suffiexs
        ss_name = ss_name.strip()
        suffixes_to_remove = [
            ' Bsp',
            ' S.G.P',
            ' S Stn',
            ' Primary Substation',
        ]
        for suffix in suffixes_to_remove:
            if ss_name.endswith(suffix):
                ss_name = ss_name[: -len(suffix)].rstrip()

        #extract voltages
        voltage_levels = {
            '6.6': None,
            '11': None,
            '33': None,
            '66': None,
            '132': None,
        }

        kv_index = ss_name.lower().rfind('kv')
        if kv_index != -1:
            ss_name = ss_name[:kv_index].rstrip()

            #extract voltages
            voltages_str = ss_name[ss_name.rfind(' ') + 1:]
            ss_name = ss_name[:ss_name.rfind(' ')]
            voltage_levels_list = voltages_str.split('/')
            for voltage_str in voltage_levels_list:
                voltage_levels[voltage_str] = True

        if ss_name.endswith('Primary Substation'):
                ss_name = ss_name[: -len(suffix)].rstrip()

        return [ss_name, voltage_levels]






