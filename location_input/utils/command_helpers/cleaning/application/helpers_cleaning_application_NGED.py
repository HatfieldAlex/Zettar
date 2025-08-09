import re
from decimal import Decimal
from pathlib import Path
import csv
import os
from django.core.management.base import CommandError

from ..helpers_cleaning_shared import normalise_name_and_extract_voltage_info

from location_input.constants import VOLTAGE_LEVELS

def clean_data_map_application_NGED(data_map):
    type_map = {
        "Primary Substation": "primary",
        "Bulk Supply Point": "bsp",
        "Grid Supply Point": "gsp",
    }

    connection_status_map = {
        "Connection offers not yet accepted": "pending",
        "Budget Estimates Provided": "budget",
        "Connection offers accepted": "accepted",
    }

    ss_type_raw = next(
        (k for k in type_map if data_map.get(k, "-") != "-"), None
    )

    ss_name, ss_voltages = normalise_name_and_extract_voltage_info(
        data_map[ss_type_raw]
    )

    ss_proposed_voltage = (
        f"{float(data_map['Proposed Connection Voltage (kV)']):.1f}"
    )

    ss_type = type_map[ss_type_raw]
    ss_dno = "NGED"
    ss_connection_status = connection_status_map[data_map["Connection Status"]]
    ss_tot_demand_num = data_map["Total Demand Number"]
    ss_tot_demand_capacity = data_map["Total Demand Capacity (MW)"]
    ss_tot_generation_num = data_map["Total Generation Number"]
    ss_tot_generation_capacity = data_map["Total Generation Capacity (MW)"]

    NGED_cleaned_data_map = {
        "name": ss_name,
        "type": ss_type,
        "dno": ss_dno,
        "ss_voltages": ss_voltages,
        "proposed_voltage": ss_proposed_voltage,
        "connection_status": ss_connection_status,
        "total_demand_number": ss_tot_demand_num,
        "total_demand_capacity_mw": ss_tot_demand_capacity,
        "total_generation_number": ss_tot_generation_num,
        "total_generation_capacity_mw": ss_tot_generation_capacity,
    }

    return NGED_cleaned_data_map



def handle_row_NGED(row, writer, successes, failures, command):
    ss_chain = {
        "gsp": row["Grid Supply Point"],
        "bsp": row["Bulk Supply Point"],
        "primary": row["Primary Substation"],
    }
    try:
        cleaned_row = clean_data_map(row, "NGED")
        writer.writerow(cleaned_row)
        command.stdout.write(command.style.SUCCESS(f"Successfully cleaned row: {ss_chain}"))
        successes.append(ss_chain)

    except Exception as e:
        command.stderr.write(command.style.ERROR(f"Error cleaning row: {ss_chain}"))
        command.stderr.write(command.style.ERROR(str(e)))
        failures.append(ss_chain)

def extract_identifier_from_row_application_NGED(row):
    identifier_name = "substation chain"
    identifier = {
        "gsp": row["Grid Supply Point"],
        "bsp": row["Bulk Supply Point"],
        "primary": row["Primary Substation"],
    }
    return (identifier_name, identifier)

__all__ = [
    "clean_data_map_application_NGED",
    "handle_row_NGED",
    "extract_identifier_from_row_application_NGED",
]
