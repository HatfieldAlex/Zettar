from django.contrib.gis.geos import Point
from ..helpers_cleaning_shared import normalise_name_and_extract_voltage_info
from ..helpers_cleaning_shared import normalise_name_and_extract_voltage_info


def clean_data_map_substation_NGED(row):
    ss_type = row["Substation Type"]
    ss_name = row["Substation Name"]
    ss_lat = row["Latitude"]
    ss_lng = row["Longitude"]

    type_map = {
        "Primary Substation": "primary",
        "Bulk Supply Point": "bsp",
        "Super Grid Substation": "gsp",
    }

    ss_dno = "NGED"
    ss_geolocation = Point(float(ss_lat), float(ss_lng))
    ss_name, ss_voltages = normalise_name_and_extract_voltage_info(
        row["Substation Name"]
    )
    ss_type = type_map[ss_type]

    cleaned_row = {
        "name": ss_name,
        "type": ss_type,
        "geolocation": ss_geolocation.wkt,
        "dno": ss_dno,
        "voltages": ss_voltages,
    }

    return cleaned_row


def extract_identifier_from_row_substation_NGED(row):
    identifier_name = "Substation Number"
    identifier = row.get("Substation Number")
    return (identifier_name, identifier)

__all__ = [
    "clean_data_map_substation_NGED",
    "extract_identifier_from_row_substation_NGED",
]
