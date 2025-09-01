from django.conf import settings
import pandas as pd 
from django.contrib.gis.geos import Point as GEOSPoint
from typing import Any, Union, Callable
from ..data_resource_class import DataResource
from .shared_helpers import normalise_name_and_extract_voltage_info
from ...models import RawFetchedDataStorage
import json
from ..data_resource_class._prepare import _CleaningHelpers

nged_substation_cleaning_helpers = _CleaningHelpers(
    extract_payload_func=lambda raw_parsed_response: raw_parsed_response["result"]["records"],

    drop_headers={"initial": {"Easting", "Northing"}, "subsequent": {"Longitude", "Latitude"}},
    exclusions={"type": {"132kv Switching Station", "Ehv Switching Station"}},
    additional_columns={"dno_group", "geolocation"},

    name_alias="Substation Name",
    type_alias="Substation Type",
    external_identifier="_id",

    primary_alias="Primary Substation",
    bsp_alias="Bulk Supply Point",
    gsp_alias="Super Grid Substation",

    row_transformation_external_identifier=lambda row: str(row["external_identifier"]),
    row_transformation_geolocation=lambda row: GEOSPoint(row.get("Latitude", 0), row.get("Longitude", 0), srid=4326),
    row_transformation_name=lambda row: normalise_name_and_extract_voltage_info(row.get("name", ""))[0],
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