from django.conf import settings
import pandas as pd 
from django.contrib.gis.geos import Point as GEOSPoint
from typing import Any, Union, Callable
from ..data_resource_class import DataResource
from .shared_helpers import normalise_name_and_extract_voltage_info
from ...models import RawFetchedDataStorage
import json

def extract_payload__nged_connection_application(raw_response):
    return raw_response.json()["result"]["records"]



headers_rename_map__nged_connection_application = {
    "Licence": "licence",
    "Proposed Connection Voltage (kV)": "proposed_voltage",
    "Connection Status": "connection_status",
    "Total Demand Number": "total_demand_number",
    "Total Demand Capacity (MW)": "total_demand_capacity_mw",
    "Total Generation Number": "total_generation_number",
    "Total Generation Capacity (MW)": "total_generation_capacity_mw",
    "Primary Substation": "primary_substation",
    "Bulk Supply Point": "bsp",
    "Grid Supply Point": "gsp",
}


new_headers__nged_connection_application = {"name", "candidate_voltage_levels_kv", "substation_type", "dno_group", "external_identifier"}

drop_headers__nged_connection_application = {"licence", "gsp", "bsp", "primary_substation"}

value_map__nged_connection_application = {
    "connection_status": {
        "Connection offers not yet accepted": "pending",
        "Budget Estimates Provided": "budget",
        "Connection offers accepted": "accepted",
    }
}

def process_row__nged_connection_application(row):
        row_primary = row["primary_substation"]
        row_bsp = row["bsp"]
        row_gsp = row["gsp"]

        if row_primary != "-":
            nged_substation_type = "primary_substation"
        elif row_bsp != "-":
            nged_substation_type = "bsp"
        else:
           nged_substation_type = "gsp"

        row["substation_type"] = nged_substation_type
        row["name"], row["candidate_voltage_levels_kv"] = normalise_name_and_extract_voltage_info(nged_substation_type)
        row["dno_group"] = "nged"
        row["external_identifier"] = f"BSP: {row_bsp}, GSP: {row_gsp}, Primary Substation: {row_primary}"

        return row



def nged_connection_application_clean(
    raw_payload_json: Union[dict[str, Any], list[dict[str, Any]]],
    log: Callable[[str, str], None] = print
    ) -> pd.DataFrame:

    #convert to dataframe
    log("Converting raw JSON payload into DataFrame...")
    df = pd.DataFrame.from_records(raw_payload_json)

    #renaming headers so universal
    log("Renaming headers to align with validation schema...")
    df.rename(columns=headers_rename_map__nged_connection_application, inplace=True)

    #adding new headers 
    log("Adding new columns for derived values...")
    for header in new_headers__nged_connection_application:
        df[header] = None

    #delete unneeded rows 
    log("Filtering out irrelevant rows...")
    #N/A

    log("Cleaning rows...")
    df = df.apply(process_row__nged_connection_application, axis=1)

    #dropping unneeded headers
    log("Dropping unnessary columns to align with validation schema...")
    df.drop(columns=drop_headers__nged_connection_application, inplace=True)

    #rename data values
    log("Mapping specific cell values to standardised terms...")
    for column, value_map in value_map__nged_connection_application.items():
        df[column] = df[column].replace(value_map)

    return df







    

nged_connection_application_data_resource = DataResource(
    reference="nged_connection_application",
    base_url="https://connecteddata.nationalgrid.co.uk/api/3/action",
    dno_group="nged",
    data_category="connection_application",
    path="datastore_search",
    query_params={
        "resource_id": "b03b02bf-ac69-44fa-a3af-2d69cdccdcb0",
        "limit": 1300,
    },
    headers={"Authorization": f"{settings.NGED_API_KEY}"},
    clean_func=nged_connection_application_clean,
    extract_payload_func=extract_payload__nged_connection_application,
)


__all__ = ["nged_connection_application_data_resource"]