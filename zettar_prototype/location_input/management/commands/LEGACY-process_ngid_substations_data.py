import csv 
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point 
import requests
import io
import re
from location_input.utils.command_helpers import normalise_name_and_extract_voltage_info
from location_input.models.shared_fields import ConnectionVoltageLevel 
from location_input.models.substations import (
    DNOGroup,
    GSPSubstation,
    BSPSubstation,
    PrimarySubstation,
)



class Command(BaseCommand):
    help = 'Import and process ngid data from ngid website'

    def handle(self, *args, **options):

        self.clear_existing_nged_substations_data()

        self.stdout.write(f"Fetching CSV ...")
        CSV_PATH = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'ngid' / 'substation_locations_raw.csv'

        success_ids = []
        failure_ids = []

        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                if row['Substation Type'] in {'132kv Switching Station', 'Ehv Switching Station'}:
                    continue
                substation_number = row.get('Substation Number')
                try:
                    self.process_row(row)           
                    self.stdout.write(self.style.SUCCESS(f"Successfully processed row with substationID {substation_number}"))
                    success_ids.append(substation_number)
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error processing row of substationID: {substation_number}"))
                    self.stderr.write(self.style.ERROR(str(e)))
                    failure_ids.append(substation_number)

        self.stdout.write(self.style.SUCCESS(
            f"CSV import complete: {len(success_ids)} succeeded, {len(failure_ids)} failed."
        ))

        if failure_ids:
            failed_list = ', '.join(failure_ids)
            self.stderr.write(self.style.ERROR(f"Failed substationIDs: {failed_list}"))


    def clear_existing_nged_substations_data(self):
        self.stdout.write("Clearing existing NGED substation data...")
        dno_group = DNOGroup.objects.get(abbr="NGED")
        PrimarySubstation.objects.filter(dno_group=dno_group).delete()
        BSPSubstation.objects.filter(dno_group=dno_group).delete()
        GSPSubstation.objects.filter(dno_group=dno_group).delete()
        self.stdout.write("NGED substation data cleared")

    def process_row(self, row):
        
        ss_type = row['Substation Type']
        ss_name = row['Substation Name']
        ss_lat = row['Latitude']
        ss_lng = row['Longitude']
        try:
            ss_geolocation = Point(float(ss_lat), float(ss_lng))
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid latitude ({ss_lat}), longitude ({ss_lng})")

        #handling licence stuff
        dno_group_obj= DNOGroup.objects.get(abbr="NGED")


        ss_name, ss_voltages = normalise_name_and_extract_voltage_info(ss_name)
        connection_voltage_levels_objs = ConnectionVoltageLevel.objects.filter(level_kv__in=ss_voltages)

        if ss_type == 'Primary Substation':
            primary_ss = PrimarySubstation.objects.create(
                name=ss_name,
                geolocation=ss_geolocation,
                dno_group=dno_group_obj,
            )
            primary_ss.voltage_kv.set(connection_voltage_levels_objs)
            primary_ss.save()

        elif ss_type == 'Bulk Supply Point':
            bsp_ss = BSPSubstation.objects.create(
                name=ss_name,
                geolocation=ss_geolocation,
                dno_group=dno_group_obj,
            )
            bsp_ss.voltage_kv.set(connection_voltage_levels_objs)
            bsp_ss.save()
        
        elif ss_type == 'Super Grid Substation':
            gsp_ss = GSPSubstation.objects.create(
                name=ss_name,
                geolocation=ss_geolocation,
                dno_group=dno_group_obj,
            )
            gsp_ss.voltage_kv.set(connection_voltage_levels_objs)
            gsp_ss.save()