from django.conf import settings
import pandas as pd 
from django.contrib.gis.geos import Point as GEOSPoint
from typing import Any, Union, Callable
from ..data_resource_class import DataResource
from .utils import normalise_raw_name_entry, substation_type_map
from ...models import RawFetchedDataStorage
import json
from ..data_resource_class._prepare import _CleaningHelpers



nged_substation_cleaning_helpers = _CleaningHelpers(
    extract_payload_func=lambda raw_parsed_response: raw_parsed_response["result"]["records"],
    drop_headers={"initial": {"Easting", "Northing"}, "subsequent": {"Substation Name", "Substation Type", "_id", "Longitude", "Latitude"}},
    exclusions={"Substation Type": {"132kv Switching Station", "Ehv Switching Station"}},

    
    construct_external_identifier=lambda row: str(row["_id"]),
    construct_geolocation=lambda row: GEOSPoint(row.get("Latitude", 0), row.get("Longitude", 0), srid=4326),
    construct_name=lambda row: normalise_raw_name_entry(row.get("Substation Name", "")),
    construct_type=lambda row: substation_type_map("Primary Substation", "Bulk Supply Point", "Super Grid Substation").get(row["Substation Type"], "unknown"), 
)

nged_substation_data_resource = DataResource(
    reference="nged_substation",
    base_url="https://connecteddata.nationalgrid.co.uk/api/3/action",
    dno_group="nged",
    data_category="substation",
    path="datastore_search",
    query_params={
        "resource_id": "e06413f8-0d86-4a13-b5c5-db14829940ed",
        "limit": 2500,
    },
    headers={"Authorization": f"{settings.NGED_API_KEY}"},
    cleaning_helpers=nged_substation_cleaning_helpers,
)

__all__ = ["nged_substation_data_resource"]