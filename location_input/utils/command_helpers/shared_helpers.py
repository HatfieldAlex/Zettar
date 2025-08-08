from pathlib import Path
import csv
import os
from django.core.management.base import CommandError
from location_input.utils.command_helpers.command_helpers import normalise_name_and_extract_voltage_info

def open_csv(path, mode):
    return open(path, mode, encoding="utf-8", newline="")

def get_data_csv_path(data_stage, dno_group_abbr):
    return (
        Path(__file__).resolve().parent.parent.parent.parent 
            / "data"
            / f"{data_stage}"
            / f"connection_applications_{data_stage}_{dno_group_abbr}.csv"
    )


def reset_csv(file_path, csv_headers, stdout):
    """
    Deletes an existing CSV (if it exists) and creates a new blank one 
    with the given headers. Raises CommandError on failure.
    """
    try:
        # Remove existing file if present
        if file_path.exists():
            stdout.write(f"Removing old CSV: {file_path}")
            file_path.unlink()

        # Ensure parent directory exists
        os.makedirs(file_path.parent, exist_ok=True)

        # Create blank CSV with headers
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=csv_headers)
            writer.writeheader()

        stdout.write(f"Blank CSV initialised: {file_path.name}")

    except Exception as e:
        raise CommandError(f"Error resetting CSV {file_path}: {e}")

def clean_data_map(data_map, category):
    if category == 'NGED':
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
        ss_dno = category
        ss_connection_status = connection_status_map[data_map["Connection Status"]]
        ss_tot_demand_num = data_map["Total Demand Number"]
        ss_tot_demand_capacity = data_map["Total Demand Capacity (MW)"]
        ss_tot_generation_num = data_map["Total Generation Number"]
        ss_tot_generation_capacity = data_map["Total Generation Capacity (MW)"]

    cleaned_data_map = {
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

    return cleaned_data_map

