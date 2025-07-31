import csv 
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point 
import requests
import io

from location_input.models.substations import (
    DNOGroup,
    DNOLicenceArea,
    GSPSubstation,
    BSPSubstation,
    PrimarySubstation,
)

class Command(BaseCommand):
    help = 'Import and process ngid data from ngid website'

    def handle(self, *args, **options):
        self.stdout.write("Clearing existing NGED substation data...")
        PrimarySubstation.objects.filter(
            bsp_substation__gsp_substation__licence_area__dno_group__abbreviation='NGED'
        ).delete()
        BSPSubstation.objects.filter(
            gsp_substation__licence_area__dno_group__abbreviation='NGED'
        ).delete()
        GSPSubstation.objects.filter(licence_area__dno_group__abbreviation='NGED').delete()
        self.stdout.write("NGED substation data cleared")



        self.stdout.write(f"Fetching CSV ...")
        CSV_PATH = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'ngid' / 'network_opportunity_map_headroom.csv'

        success_ids = []
        failure_ids = []

        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                if row['type'] == 'Secondary':
                    continue

                try:
                    self.process_row(row)
                    substation_id = row.get('substationID')
                    self.stdout.write(self.style.SUCCESS(f"Successfully processed row with substationID {substation_id}"))
                    success_ids.append(substation_id)
                except Exception as e:
                    substation_id = row.get('substationID')
                    self.stderr.write(self.style.ERROR(f"Error processing row of substationID: {substation_id}"))
                    self.stderr.write(self.style.ERROR(str(e)))
                    failure_ids.append(substation_id)

        self.stdout.write(self.style.SUCCESS(
            f"CSV import complete: {len(success_ids)} succeeded, {len(failure_ids)} failed."
        ))

        if failure_ids:
            failed_list = ', '.join(failure_ids)
            self.stderr.write(self.style.ERROR(f"Failed substationIDs: {failed_list}"))

    def process_row(self, row):
        substation_type = row['type']
        name = row['name']
        primary_substation_name = row['primary']
        bsp_substation_name = row['BSP']
        gsp_substation_name = row['GSP']
        lat = row['latitude']
        lng = row['longitude']
        try:
            geolocation = Point(float(lat), float(lng))
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid latitude ({lat}), longitude ({lng})")


        licence_area = row['area'].strip().lower().replace(' ', '_')

        #handling GSP level and licence stuff
        licence_area_obj = DNOLicenceArea.objects.get(licence_area=licence_area)
        gsp_substation_obj, created_gsp = GSPSubstation.objects.get_or_create(
            name=gsp_substation_name,
            licence_area=licence_area_obj,
            )

        #handling BSP level
        bsp_substation_object_name = bsp_substation_name if bsp_substation_name else name
        bsp_substation_object_geolocation = None if bsp_substation_name else geolocation

        bsp_substation_obj, created_bsp = BSPSubstation.objects.get_or_create(
            name=bsp_substation_object_name,
            gsp_substation=gsp_substation_obj,
        )

        if created_bsp and bsp_substation_object_geolocation:
            bsp_substation_obj.geolocation = bsp_substation_object_geolocation
            bsp_substation_obj.save()

        #handling Primary level
        if substation_type == 'Primary':
            primary_substation_obj, created_primary = PrimarySubstation.objects.get_or_create(
                name=name,
                geolocation=geolocation,
                bsp_substation=bsp_substation_obj
            )




