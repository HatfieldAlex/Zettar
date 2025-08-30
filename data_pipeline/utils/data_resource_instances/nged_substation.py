from django.conf import settings
import pandas as pd 
from django.contrib.gis.geos import Point as GEOSPoint
from typing import Any, Union, Callable
from ..data_resource_class import DataResource
from .shared_helpers import normalise_name_and_extract_voltage_info
from ...models import RawFetchedDataStorage
import json
from ..data_resource_class._prepare import _CleaningHelpers


def row_transformation_external_identifier_nged_substation(row):
    return str(row["external_identifier"])

def row_transformation_geolocation_nged_substation(row):
    return GEOSPoint(row.get("Latitude", 0), row.get("Longitude", 0), srid=4326)

def row_transformation_name_nged_substation(row):
    return normalise_name_and_extract_voltage_info(row.get("name", ""))[0]

nged_substation_cleaning_helpers = _CleaningHelpers(
    drop_headers={"initial": {"Easting", "Northing"}, "subsequent": {"Longitude", "Latitude"}},
    exclusions={"type": {"132kv Switching Station", "Ehv Switching Station"}},
    additional_columns={"dno_group", "geolocation"},

    name_alias="Substation Name",
    type_alias="Substation Type",
    external_identifier="_id",

    primary_alias="Primary Substation",
    bsp_alias="Bulk Supply Point",
    gsp_alias="Super Grid Substation",

    row_transformation_external_identifier=row_transformation_external_identifier_nged_substation,
    row_transformation_geolocation=row_transformation_geolocation_nged_substation,
    row_transformation_name=row_transformation_name_nged_substation,
)

def extract_payload_nged_substation(raw_response):
    return raw_response.json()["result"]["records"]

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
    extract_payload_func=extract_payload_nged_substation,
)

__all__ = ["nged_substation_data_resource"]