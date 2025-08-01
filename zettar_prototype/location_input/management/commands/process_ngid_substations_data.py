import csv 
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point 
import requests
import io
import re

from location_input.models.substations import (
    DNOGroup,
    GSPSubstation,
    BSPSubstation,
    PrimarySubstation,
)

class Command(BaseCommand):
    help = 'Import and process ngid data from ngid website'

    def handle(self, *args, **options):

        self.clear_existing_nged_data()

        self.stdout.write(f"Fetching CSV ...")
        CSV_PATH = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'ngid' / 'substation_locations_raw.csv'

        success_ids = []
        failure_ids = []

        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            self.clear_existing_nged_data()

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


    def clear_existing_nged_data(self):
        self.stdout.write("Clearing existing NGED substation data...")
        dno_group = DNOGroup.objects.get(abbr="NGED")
        PrimarySubstation.objects.filter(dno_group=dno_group).delete()
        BSPSubstation.objects.filter(dno_group=dno_group).delete()
        GSPSubstation.objects.filter(dno_group=dno_group).delete()
        self.stdout.write("NGED substation data cleared")


    def process_row(self, row):
        
        substation_type = row['Substation Type']
        name = row['Substation Name']
        lat = row['Latitude']
        lng = row['Longitude']
        try:
            geolocation = Point(float(lat), float(lng))
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid latitude ({lat}), longitude ({lng})")

        #handling licence stuff
        dno_group_obj= DNOGroup.objects.get(abbr="NGED")


        for i, c in enumerate(name):
            if c.isdigit():
                name = name[:i-1]
                break

        if substation_type == 'Primary Substation':
            if name.endswith(' Primary Substation'):
                name = name.removesuffix(' Primary Substation')
            PrimarySubstation.objects.create(
                name=name,
                geolocation=geolocation,
                dno_group=dno_group_obj,
            )

        elif substation_type == 'Bulk Supply Point':
            if name.endswith(' Bsp'):
                name = name.removesuffix(' Bsp')
            if name.endswith(' ('):
                name = name.removesuffix(' (')
            BSPSubstation.objects.create(
                name=name,
                geolocation=geolocation,
                dno_group=dno_group_obj,
            )
        
        elif substation_type == 'Super Grid Substation':
            if name.endswith(' S.G.P'):
                name = name.removesuffix(' Sgp')
            if name.endswith(' ('):
                name = name.removesuffix(' (')
            GSPSubstation.objects.create(
                name=name,
                geolocation=geolocation,
                dno_group=dno_group_obj,
            )



