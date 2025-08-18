from django.conf import settings
import pandas as pd 
from shapely.geometry import Point
from typing import Any, Union
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

def nged_substation_clean(raw_response: Union[dict[str, Any], list[dict[str, Any]]]) -> pd.DataFrame:
    print(raw_response.keys())
    json_object = raw_response.json()
    payload = json_object["result"]["records"]
    
    print(payload)


    df = pd.DataFrame.from_records(payload)
    df = df.rename(columns=nged_headers_rename_map)
    df = df[~df["type"].isin(drop_types)]
    df["type"] = df["type"].map(nged_field_type_aliases_map)
    df["geolocation"] = df.apply(lambda row: Point(row["longitude"], row["latitude"]), axis=1)
    df.drop(columns=["longitude", "latitude"], inplace=True)
    df[["name", "candidate_voltage_levels_kv"]] = df["name"].apply(
        lambda n: pd.Series(normalise_name_and_extract_voltage_info(n)))
    df["dno"] = "nged"

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
    raw_data_storage_id=latest_raw_data.id if latest_raw_data else None,
)

__all__ = ["nged_substation_data_resource"]