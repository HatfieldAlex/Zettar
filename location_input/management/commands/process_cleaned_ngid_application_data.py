import csv
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import Point
import requests
import io
import re
from location_input.utils.command_helpers import (
    normalise_name_and_extract_voltage_info,
)
from location_input.models.shared_fields import ConnectionVoltageLevel
import ast
from django.contrib.gis.geos import GEOSGeometry
from datetime import date
from location_input.models.new_connections import (
    NewConnection,
    ConnectionStatus,
    ReportingPeriod,
)
from location_input.models.substations import DNOGroup, Substation

class Command(BaseCommand):
    help = "Process cleaned ngid application data"

    def handle(self, *args, **options):

        self.clear_existing_cleaned_nged_application_data()
        self.stdout.write(f"Fetching CSV ...")
        CSV_PATH = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "data"
            / "ngid"
            / "clean"
            / "ngid_connection_applications_clean.csv"
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
                f"CSV processing complete: {len(success_ss_names)} succeeded, {len(failure_ss_names)} failed."
            )
        )

        if failure_ss_names:
            failed_list = ", ".join(failure_ss_names)
            self.stderr.write(
                self.style.ERROR(f"Failed substation names: {failed_list}")
            )

    def clear_existing_cleaned_nged_application_data(self):
        self.stdout.write("Clearing existing NGED New Connection data...")
        dno_group = DNOGroup.objects.get(abbr="NGED")
        NewConnection.objects.filter(dno_group=dno_group).delete()
        self.stdout.write("NGED New Connection data cleared")

    def process_row(self, row):

        # finding variables
        ss_name = row["name"]
        ss_type = row["type"]
        ss_dno = row["dno"]
        ss_voltages = ast.literal_eval(row["ss_voltages"])
        connection_voltage_level = row["proposed_voltage"]
        ss_connection_status = row["connection_status"]
        ss_total_demand_number = row["total_demand_number"]
        ss_total_demand_capacity = row["total_demand_capacity_mw"]
        ss_total_generation_number = row["total_generation_number"]
        ss_total_generation_capacity = row["total_generation_capacity_mw"]

        # finding object instances
        connection_status_obj = ConnectionStatus.objects.get(
            status=ss_connection_status
        )

        print(f"connection_voltage_level type: {connection_voltage_level}")
        proposed_voltage_level_obj = ConnectionVoltageLevel.objects.get(
            level_kv=connection_voltage_level
        )

        reporting_period_obj = ReportingPeriod.objects.get(
            start_date=date(2025, 1, 1), end_date=date(2025, 5, 31)
        )
        dno_group_obj = DNOGroup.objects.get(abbr=ss_dno)

        new_connection = NewConnection.objects.create(
            connection_status=connection_status_obj,
            connection_voltage_level=proposed_voltage_level_obj,
            reporting_period=reporting_period_obj,
            dno_group=dno_group_obj,
            demand_count=ss_total_demand_number,
            total_demand_capacity_mw=ss_total_demand_capacity,
            generation_count=ss_total_generation_number,
            total_generation_capacity_mw=ss_total_generation_capacity,
        )


        # finding substation obj - challenge is that there may be many be many so we have to isolate by voltage lvl
        try:
            substation_obj = Substation.objects.get(
                name=ss_name,
                dno_group=dno_group_obj,
                type=ss_type,
            )
        except:
            substations_with_ss_name = Substation.objects.filter(name=ss_name)
            for candidate_ss in substations_with_ss_name:
                candidate_ss_voltages_qs = candidate_ss.voltage_kv.order_by(
                    "level_kv"
                ).values_list("level_kv", flat=True)
                candidate_ss_voltages_list = list(candidate_ss_voltages_qs)
                if candidate_ss_voltages_list == ss_voltages:
                    substation_obj = candidate_ss

        setattr(new_connection, "substation", substation_obj)

        new_connection.save()


# #edge case connections that need to be managed:
# Failed substation names: Coventry West, Jaguar Cars Browns Lane, Harbury, Clifton, Grantham, Skegness, Sleaford, Chesterfield, Alfreton, Annesley, Clipstone, Goitside, Mansfield, Staveley, Whitwell, Daventry, Hinckley, Nuneaton, Pailton, Burton, Gresley, Ashby, Victoria Road, Bradwell Abbey, Stony Stratford, Coalville, Leicester East, Corby, Irthlingborough, Kettering, Melton Mowbray, Northampton East, Oakham, Wellingborough, Tamworth, Clifton, Toton 3, Willoughby, Staythorpe C, Checkerhouse, Hawton, Staythorpe B, Nottingham East, Nottingham North, Boston, South Holland, Crown Fm, Stamford, Lincoln Main No 1, Rookery Lane Lincoln, Worksop, Derby South, Heanor, Stanton, Uttoxeter, Winster, Skegness, Chesterfield, Annesley, Crown Fm, Coventry North, Hinckley, Rugby, Ashby, Stony Stratford, Coalville, Irthlingborough, Kettering, Northampton, Northampton East, Oakham, Wellingborough / (Reserve), Tamworth, Tamworth Town, Loughborough, Staythorpe C, Derby South, Courthouse Green, Courthouse Green, Harbury, Alfreton, Annesley, Clipstone, Staveley, Whitwell, Pailton, Rugby, Ashby, Stony Stratford, Mantle Lane Coalville, Irthlingborough, Kettering, Melton Mowbray, Northampton, Northampton East, Loughborough, Clifton, Hawton, Nottingham East, Nottingham North, Rookery Lane Lincoln, Worksop, Derby South, Rover Way, Golden Hill, Pyle, Hirwaun, Llanarth, Rhos, Swansea North, Merthyr East, Pontyclun, Talbot Green, Cardiff South Grid, Rover Way, Waterton Industrial, Tir John, Pontyclun, Talbot Green, Magor, Cardiff South Grid, Britton Ferry, Morriston, Swansea North, Travellers Rest, Pencoed, Magor, Indian Queens, Feeder Road, Indian Queens, Indian Queens, Stourport, Warndon, Worcester, Bushbury B-C, Bustleholm, Rushall, Smethwick, Winson Green, Boothen, Meaford C, Stagefields, Banbury, Clifton, Ryeford, Ketley, Bartley Green, Halesowen, Rednal, Shirley, Solihull, Boughton Road, Nechells West, Sparkbrook, Birchfield Lane, Oldbury B, Tividale, Coseley, Dudley, Hinksford, Lye, Wolverhampton West, Woodside, Eastern Avenue, Montpellier, Tewkesbury Grid, Rugeley, Burntwood, Lichfield, Willenhall, Wolverhampton, Kidderminster, Timberdine, Upton Warren, Warndon, Bushbury B-C, Stafford, Wednesfield, Bustleholm, Kingstanding / Dummy, Ladywood, Smethwick, Winson Green, Boothen, Burslem, Banbury, Clifton, Rednal, Selly Oak, Sutton Coldfield, Castle Bromwich, Chester Street, Nechells West, Sparkbrook, Tividale, Cheltenham, Tewkesbury Grid, Rugeley, Lichfield, Shrewsbury, Wolverhampton, Kidderminster, Malvern, Timberdine, Upton Warren, Warndon, Bushbury B-C, Stafford, Wednesfield, Bustleholm, Kingstanding / Dummy, Ladywood, Perry Barr, Rushall, Smethwick, Winson Green, Boothen, Burslem, Stagefields, Banbury, Feckenham, Ketley, Chad Valley, Highters Heath, Rednal, Elmdon, Hams Hall South, Shirley, Sutton Coldfield, Bordesley, Boughton Road, Castle Bromwich, Cheapside, Chester Street, Nechells West, Hockley, Summer Lane, Black Lake, Birchfield Lane, Oldbury B, Tividale, Coseley, Lye, Woodside, Cheltenham, Eastern Avenue, Marle Hill, Tewkesbury Grid, Rugeley, Burntwood, Lichfield, Shrewsbury, Bentley, Wolverhampton