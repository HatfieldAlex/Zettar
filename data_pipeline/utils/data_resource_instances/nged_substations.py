from django.conf import settings
import pandas as pd 
from django.contrib.gis.geos import Point as GEOSPoint
from typing import Any, Union, Callable
from ..data_resource_class import DataResource
from .shared_helpers import normalise_name_and_extract_voltage_info
from ...models import RawFetchedDataStorage
import json

nged_field_type_aliases_map = {
        "Primary Substation": "primary",
        "Bulk Supply Point": "bsp",
        "Super Grid Substation": "gsp",
    }

nged_headers_rename_map = {
        "Substation Number": "external_identifier",
        "Substation Name": "name",
        "Substation Type": "type",
        "Latitude": "latitude",
        "Longitude": "longitude",
    }

drop_types = {"132kv Switching Station", "Ehv Switching Station"}

initial_drop_headers = ["_id", "Easting", "Northing"]

def extract_payload_nged_substation(raw_response):
    return raw_response.json()["result"]["records"]


def nged_substation_clean(
    raw_payload_json: Union[dict[str, Any], list[dict[str, Any]]],
    log: Callable[[str, str], None] = print
    ) -> pd.DataFrame:

    log("Converting raw JSON payload into DataFrame...")
    df = pd.DataFrame.from_records(raw_payload_json)

    log("Dropping columns not required...")
    df.drop(columns=initial_drop_headers, inplace=True)

    log("Filtering out non-substation types (i.e., switching stations)...")
    df = df[~df["Substation Type"].isin(drop_types)]  

    log("Generating 'geolocation' column as GEOS Point objects using longitude and latitude, and dropping the original columns...")
    df["geolocation"] = df.apply(lambda r: GEOSPoint(r["Longitude"], r["Latitude"], srid=4326),axis=1)
    df.drop(columns=["Longitude", "Latitude"], inplace=True)

    log("Renaming headers to align with validation schema")
    df = df.rename(columns=nged_headers_rename_map)

    log("Standardising substation type labels for consistency...")
    df["type"] = df["type"].map(nged_field_type_aliases_map)
  
    log("Normalising substation names and extracting voltage level candidates (in kV)...")
    df[["name", "candidate_voltage_levels_kv"]] = df["name"].apply(
        lambda n: pd.Series(normalise_name_and_extract_voltage_info(n)))
    
    log("Assigning DNO group identifier to each record...")
    df["dno_group"] = "nged"

    log("Stringifying the external_identifier...")
    df["external_identifier"] = df.apply(lambda r: str(r["external_identifier"]), axis=1)

    print(df.columns)

    return df

latest_raw_data = (
    RawFetchedDataStorage.objects
    .filter(
        dno_group="nged",
        data_category="substation",
        source_url="https://connecteddata.nationalgrid.co.uk/api/3/action/datastore_search",
    )
    .order_by("-fetched_at")
    .first()
)


nged_substation_data_resource = DataResource(
    base_url="https://connecteddata.nationalgrid.co.uk/api/3/action",
    dno_group="nged",
    data_category="substation",
    path="datastore_search",
    query_params={
        "resource_id": "e06413f8-0d86-4a13-b5c5-db14829940ed",
        "limit": 2500,
    },
    headers={"Authorization": f"{settings.NGED_API_KEY}"},
    clean_func=nged_substation_clean,
    current_raw_data_storage_id=latest_raw_data.id if latest_raw_data else None,
    extract_payload_func=extract_payload_nged_substation,
)


__all__ = ["nged_substation_data_resource"]