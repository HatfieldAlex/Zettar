import csv
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point
import requests
import io
import re
from location_input.utils.command_helpers import normalise_name_and_extract_voltage_info
from location_input.models.shared_fields import ConnectionVoltageLevel
import ast
from django.contrib.gis.geos import GEOSGeometry
from location_input.models.substations import (
    DNOGroup,
    GSPSubstation,
    BSPSubstation,
    PrimarySubstation,
)


class Command(BaseCommand):
    help = "Process cleaned ngid data"

    def handle(self, *args, **options):

        self.clear_existing_cleaned_nged_substation_data()

        self.stdout.write(f"Fetching CSV ...")
        CSV_PATH = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "data"
            / "ngid"
            / "clean"
            / "ngid_substations_locations_clean.csv"
        )

        success_ss_names = []
        failure_ss_names = []

        with open(CSV_PATH, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                substation_name = row["name"]
                try:
                    self.process_row(row)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully processed row with substation name {substation_name}"
                        )
                    )
                    success_ss_names.append(substation_name)
                except Exception as e:
                    self.stderr.write(
                        self.style.ERROR(
                            f"Error processing row  with substation name: {substation_name}"
                        )
                    )
                    self.stderr.write(self.style.ERROR(str(e)))
                    failure_ss_names.append(substation_name)

        self.stdout.write(
            self.style.SUCCESS(
                f"CSV import complete: {len(success_ss_names)} succeeded, {len(failure_ss_names)} failed."
            )
        )

        if failure_ss_names:
            failed_list = ", ".join(failure_ss_names)
            self.stderr.write(
                self.style.ERROR(f"Failed substation names: {failed_list}")
            )

    def clear_existing_cleaned_nged_substation_data(self):
        self.stdout.write("Clearing existing cleaned NGED substation data...")
        dno_group = DNOGroup.objects.get(abbr="NGED")
        PrimarySubstation.objects.filter(dno_group=dno_group).delete()
        BSPSubstation.objects.filter(dno_group=dno_group).delete()
        GSPSubstation.objects.filter(dno_group=dno_group).delete()
        self.stdout.write("Previous NGED substation data cleared")

    def process_row(self, row):

        ss_name = row["name"]
        ss_type = row["type"]
        ss_geolocation = GEOSGeometry(row["geolocation"])
        ss_dno = row["dno"]
        ss_voltages = ast.literal_eval(row["voltages"])

        substation_model_map = {
            "primary": PrimarySubstation,
            "bsp": BSPSubstation,
            "gsp": GSPSubstation,
        }

        model_class = substation_model_map.get(ss_type)
        dno_group_obj = DNOGroup.objects.get(abbr=ss_dno)
        connection_voltage_levels_objs = ConnectionVoltageLevel.objects.filter(
            level_kv__in=ss_voltages
        )

        if model_class:
            substation = model_class.objects.create(
                name=ss_name,
                geolocation=ss_geolocation,
                dno_group=dno_group_obj,
            )
            substation.voltage_kv.set(connection_voltage_levels_objs)
            substation.save()
