import ast
from django.contrib.gis.geos import GEOSGeometry

from location_input.models.substations import DNOGroup, Substation
from location_input.models.shared_fields import ConnectionVoltageLevel
from location_input.models.new_connections import (
    NewConnection,
    ConnectionStatus,
    ReportingPeriod,
    ConnectionVoltageLevel,
)

import ast
from datetime import date


def process_row_application_NGED(row):

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

def clear_existing_cleaned_application_data_NGED(dno_group_abbr, stdout):
    stdout.write(f"Clearing existing {dno_group_abbr} New Connection data...")
    dno_group = DNOGroup.objects.get(abbr=dno_group_abbr)
    NewConnection.objects.filter(dno_group=dno_group).delete()
    stdout.write(f"{dno_group_abbr} New Connection data cleared")


def clear_existing_cleaned_nged_substation_data_NGED(stdout):
    stdout.write("Clearing existing cleaned NGED substation data...")
    dno_group = DNOGroup.objects.get(abbr="NGED")
    Substation.objects.filter(dno_group=dno_group).delete()
    stdout.write("Previous NGED substation data cleared")

def process_row_NGED(row):
    ss_name = row["name"]
    ss_type = row["type"]
    ss_geolocation = GEOSGeometry(row["geolocation"])
    ss_dno = row["dno"]
    ss_voltages = ast.literal_eval(row["voltages"])

    dno_group_obj = DNOGroup.objects.get(abbr=ss_dno)
    connection_voltage_levels_objs = ConnectionVoltageLevel.objects.filter(
        level_kv__in=ss_voltages
    )

    substation = Substation.objects.create(
        name=ss_name,
        geolocation=ss_geolocation,
        type=ss_type,
        dno_group=dno_group_obj,
    )
    substation.voltage_kv.set(connection_voltage_levels_objs)
    substation.save()


def handle_row_process_NGED(row, successes, failures, command):
    identifier_name = row["name"]
    try:
        process_row_NGED(row)
        command.stdout.write(command.style.SUCCESS(f"Successfully processed row with substation name {identifier_name}"))
        successes.append(identifier_name)
    except Exception as e:
        command.stderr.write(command.style.ERROR(f"Error processing row  with substation name: {identifier_name}"))
        command.stderr.write(command.style.ERROR(str(e)))
        failures.append(identifier_name)


def handle_row_process_application_NGED(style, row, successful_identifiers, failed_identifiers, stdout, stderr):
    substation_name = row["name"]
    try:
        process_row_application_NGED(row)
        stdout.write(style.SUCCESS(f"Successfully processed row with substation name: {substation_name}"))
        successful_identifiers.append(substation_name)
    except Exception as e:
        stderr.write(style.ERROR(f"Error processing row  with substation name: {substation_name}"))
        stderr.write(style.ERROR(str(e)))
        failed_identifiers.append(substation_name)

