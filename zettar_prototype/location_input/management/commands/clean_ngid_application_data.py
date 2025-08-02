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
from location_input.utils.constants import VOLTAGE_CHOICES

class Command(BaseCommand):
    help = 'Import and clean ngid application data from ngid website'

    
    cleaned_csv_headers = [
                'name', 
                'type', 
                'dno', 
                'ss_voltages', 
                'proposed_voltage',
                'connection_status',
                'total_demand_number',
                'total_demand_capacity_mw',
                'total_generation_number',
                'total_generation_capacity_mw',                
                ]
    data_dir_path = Path(__file__).resolve().parent.parent.parent.parent / 'data'

    def handle(self, *args, **options):

        clean_csv_path = self.data_dir_path / 'ngid' / 'clean' / 'ngid_connection_applications_clean.csv'

        self.clear_existing_nged_substations_data(clean_csv_path)
        self.initialise_blank_csv(clean_csv_path)

        raw_csv_path = self.data_dir_path / 'ngid' / 'raw' / 'ngid_connection_applications_raw.csv'

        success_ss_app_name = []
        failure_ss_app_name = []

        with open(raw_csv_path, 'r', encoding='utf-8') as infile, \
        open(clean_csv_path, 'a', encoding='utf-8', newline='') as outfile:

            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=self.cleaned_csv_headers)

            for row in reader:
                ss_chain = {'gsp': row['Grid Supply Point'], 'bsp': row['Bulk Supply Point'], 'primary': row['Primary Substation']}
                try:
                    cleaned_row = self.clean_row(row)
                    writer.writerow(cleaned_row)           
                    self.stdout.write(self.style.SUCCESS(f"Successfully cleaned row: {ss_chain}"))
                    success_ss_app_name.append(ss_chain)
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error cleaning row: {ss_chain}"))
                    self.stderr.write(self.style.ERROR(str(e)))
                    failure_ss_app_name.append(ss_chain)

        self.stdout.write(self.style.SUCCESS(
            f"raw connection applications CSV clean complete: {len(success_ss_app_name)} succeeded, {len(failure_ss_app_name)} failed."
        ))

        if failure_ss_app_name:
            self.stderr.write(self.style.ERROR(f"Failed substation applications: {failure_ss_app_name}"))

    def clear_existing_nged_substations_data(self, PATH):
        if PATH.exists():
            self.stdout.write("Removing previous cleaned NGED substation data csv...")
            PATH.unlink()
            self.stdout.write("...cleaned NGED substation data csv removed.")

    def initialise_blank_csv(self, PATH):
        self.stdout.write(f"Creating blank CSV...")
        os.makedirs(os.path.dirname(PATH), exist_ok=True)
        with open(PATH, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.cleaned_csv_headers)
            writer.writeheader()
        self.stdout.write(f"Cleaned CSV initialised: {PATH.name}")


    def clean_row(self, row):       
        type_map = {
            'Primary Substation': 'primary',
            'Bulk Supply Point': 'bsp',
            'Grid Supply Point': 'gsp',
        }

        connection_status_map = {
            'Connection offers not yet accepted': 'pending',
            'Budget Estimates Provided': 'budget',
            'Connection offers accepted': 'accepted',
        } 

        ss_type_raw = next((k for k in type_map if row.get(k, '-') != '-'), None)

        ss_name, ss_voltages = normalise_name_and_extract_voltage_info(row[ss_type_raw])
        ss_proposed_voltage = row['Proposed Connection Voltage (kV)']
        ss_type = type_map[ss_type_raw]
        ss_dno = 'NGED'
        ss_connection_status = connection_status_map[row['Connection Status']]
        ss_tot_demand_num = row['Total Demand Number']
        ss_tot_demand_capacity = row['Total Demand Capacity (MW)']
        ss_tot_generation_num = row['Total Generation Number']
        ss_tot_generation_capacity = row['Total Generation Capacity (MW)']

        cleaned_row = {
            'name': ss_name,
            'type': ss_type,
            'dno': ss_dno,
            'ss_voltages': ss_voltages,
            'proposed_voltage': ss_proposed_voltage,
            'connection_status': ss_connection_status,
            'total_demand_number': ss_tot_demand_num,
            'total_demand_capacity_mw': ss_tot_demand_capacity,
            'total_generation_number': ss_tot_generation_num,
            'total_generation_capacity_mw': ss_tot_generation_capacity,
        }

        return cleaned_row