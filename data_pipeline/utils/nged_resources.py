from zettar_prototype.location_input.utils.command_helpers_refactor.helper_functions_oop import DNO, DataResource, ResourceCleaner
from django.conf import settings
from settings import NGED_API_KEY
import pandas as pd 
from shapely.geometry import Point
from .shared_helpers import normalise_name_and_extract_voltage_info


nged_substation_cleaner = ResourceCleaner()

nged_substation_data_resource = DataResource(
    base_url="https://connecteddata.nationalgrid.co.uk/api/3/action",
    path="datastore_search",
    query_params={
        "resource_id": "e06413f8-0d86-4a13-b5c5-db14829940ed", 
        "fields": "Substation Number,Substation Name,Substation Type,Latitude,Longitude",
        "limit": 3000,
        },
    headers={"Authorization": f"{NGED_API_KEY}"},
    resource_cleaner=nged_substation_cleaner,
)

nged_substation_data_resource.fetch_data_resource()
print(nged_substation_data_resource.raw_data)

nged_field_aliases = {
        "Primary Substation": "primary",
        "Bulk Supply Point": "bsp",
        "Super Grid Substation": "gsp",

    }

rename_map = {
        "Substation Number": "raw_id",
        "Substation Name": "name",
        "Substation Type": "type",
        "Latitude": "latitude",
        "Longitude": "longitude",
    }

def nged_clean(json_object):

    
    

    type_label_type
    payload = json_object.result["records"]
    df_raw = pd.DataFrame.from_records(payload)
    df = df_raw
    
    df = df[~df["Substation Type"].isin(["132kv Switching Station", "Ehv Switching Station"])]
    normalise_name_and_extract_voltage_info

    df[["name", "voltages"]] = df_raw["name"].apply(
        lambda n: pd.Series(normalise_name_and_extract_voltage_info(n))
    )

    df["geolocation"] = df.apply(lambda row: Point(row["longitude"], row["latitude"]), axis=1)

    df["dno"] = "nged"


    ss_name, voltage_levels_ss = normalise_name_and_extract_voltage_info(name )




