import re
from decimal import Decimal
from pathlib import Path
import csv
import os
from django.core.management.base import CommandError

from location_input.constants import VOLTAGE_LEVELS

substrings_to_remove = [
        "kv",
        "kV",
        "Kv",
        "KV",
        "Bsp",
        "S.G.P.",
        "S.G.P",
        "G.S.P",
        "S Stn",
        "Primary Substation",
        "S/S",
        "S/Stn",
        "Power Station",
        "Primary",
        "National Grid Site",
        "S Stn",
        "340038",
        " tn",
        "BSP",
    ]

def normalise_name_and_extract_voltage_info(ss_name):
    """Normalises a substation name and extract voltage level information.

    This function performs the following steps:
        - Replaces certain malformed patterns (e.g., "6 6" -> "6.6").
        - Finds numeric voltage values present in the name and checks
          them against a predefined list of voltage levels.
        - Removes specified unwanted substrings from the name.
        - Expands common street abbreviations to full words.
        - Trims extra spaces and trailing punctuation.

    Args:
        ss_name (str): The original substation name.

    Returns:
        Tuple[str, List[str]]:
            A tuple containing:
                - Normalized substation name (str)
                - Sorted list of voltage levels (List[str])
    """

    voltage_levels = VOLTAGE_LEVELS

    #standardise malformed voltage spacing
    if "6 6" in ss_name:
        ss_name = ss_name.replace("6 6", "6.6")

    #extract numerical values from str name
    voltage_levels_ss = []
    for number_str in set(re.findall(r"\d+(?:\.\d+)?", ss_name)):
        number_decimal = Decimal(number_str).quantize(Decimal("0.1"))
        number_str_standardised = str(number_decimal)

        if number_str_standardised in voltage_levels:
            voltage_levels_ss.append(number_str_standardised)
            substrings_to_remove.append(number_str)

    # Remove unwanted substrings
    for sub_str in substrings_to_remove:
        ss_name = ss_name.replace(sub_str, "")

    # Normalise common abbreviations
    ss_name = re.sub(r"\bst\.?\b", "Street", ss_name, flags=re.IGNORECASE)
    ss_name = re.sub(r"\brd\.?\b", "Road", ss_name, flags=re.IGNORECASE)
    ss_name = re.sub(r"\bln\.?\b", "Lane", ss_name, flags=re.IGNORECASE)
    
    #normalise spacing and remove trailing symbols
    ss_name = re.sub(r"\s+", " ", ss_name).strip().rstrip("./& ")

    #order voltage levels numerically 
    voltage_levels_ss = sorted(voltage_levels_ss, key=float)

    return [ss_name, voltage_levels_ss]


def clean_data_map_NGED(data_map, category):
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

def extract_identifier_from_row_NGED(row, dno_group_abbr):
    identifier_name = "substation chain"
    identifier = {
        "gsp": row["Grid Supply Point"],
        "bsp": row["Bulk Supply Point"],
        "primary": row["Primary Substation"],
    }
    return (identifier_name, identifier)