from django.conf import settings
import pandas as pd 
import requests
from django.contrib.gis.geos import Point as GEOSPoint
from typing import Any, Union, Callable
from ..data_resource_class import DataResource
from .shared_helpers import normalise_name_and_extract_voltage_info
from ...models import RawFetchedDataStorage
import json
from ..data_resource_class._prepare import _CleaningHelpers
from urllib.parse import urljoin
from .helpers_open_data_soft import get_count_open_data_soft, call_limit_open_data_soft

__all__ = []

drop_headers_primary_bsp_substation = {
    "initial": {
        "sitefunctionallocation", "licencearea", "sitevoltage", "esqcroverallrisk", "gridref", 	
        "siteassetcount", "powertransformercount", "electricalassetcount", "civilassetcount", 
        "street", "suburb", "towncity", "county", "postcode",	"yearcommissioned", "datecommissioned",	
        "siteclassification", "assessmentdate", "last_report", "calculatedresistance", "northing",	
        "measuredresistance_ohm", "next_assessmentdate", "easting",  "transratingwinter",
        "transratingsummer", "reversepower", "maxdemandsummer", "maxdemandwinter",	
        "local_authority", "local_authority_code"
    },
    "subsequent": {}
}

ukpn_primary_bsp_substation_cleaning_helpers = _CleaningHelpers(
    extract_payload_func=lambda raw_parsed_response: raw_parsed_response["results"],

    drop_headers=drop_headers_primary_bsp_substation,
    exclusions={},
    additional_columns={},

    name_alias="sitename",
    type_alias="sitetype",
    external_identifier="what3words",

    primary_alias="Primary Substation",
    bsp_alias="Grid Substation",
    gsp_alias="",

    row_transformation_external_identifier=lambda row: f"{row['name']} | {row['external_identifier']}",
    row_transformation_geolocation=lambda row: GEOSPoint(
        row["spatial_coordinates"]["lon"], 
        row["spatial_coordinates"]["lat"], 
        srid=4326
        ),
    row_transformation_name=lambda row: normalise_name_and_extract_voltage_info(row.get("name", ""))[0],
)

base_url_ukpn="https://ukpowernetworks.opendatasoft.com"
path_ukpn_primary_bsp="/api/explore/v2.1/catalog/datasets/grid-and-primary-sites/records"


def create_data_resource(offset):
    return DataResource(
        reference=f"ukpn_substation_primary_bsp_{offset}_{offset + 100}",
        base_url=base_url_ukpn,
        dno_group="ukpn",
        data_category="substation",
        path=path_ukpn_primary_bsp,
        query_params={
            "limit": 100,
            "offset": offset,
            "order_by": "sitename",
        },
        headers={"Authorization": f"Apikey {settings.UKPN_API_KEY}"},
        cleaning_helpers=ukpn_primary_bsp_substation_cleaning_helpers,
        parse_raw_response_func=lambda raw_resp: raw_resp.json()
    )

count = get_count_open_data_soft(base_url_ukpn, path_ukpn_primary_bsp)

for offset in range(0, count, call_limit_open_data_soft):
    data_resource_name = f"ukpn_primary_bsp_substation_data_resource_{offset}_{min(offset + call_limit_open_data_soft, count)}"
    globals()[data_resource_name] = create_data_resource(offset)
    __all__.append(data_resource_name)




drop_headers_gsp_substation = {
    "initial": {
        "dno", "floc", "minimum_observed_power_flow", "maximum_observed_power_flow",
        "asset_import_limit", "asset_export_limit", "technical_limit_import_summer", 
        "technical_limit_import_winter","technical_limit_import_access_period", 
        "technical_limit_export", "export_capacity_utilisation",
        "import_capacity_utilisation", "technical_limits_available"
    },   
    "subsequent": {
        "geo_point_2d"
    },
}

ukpn_gsp_substation_cleaning_helpers = _CleaningHelpers(
    extract_payload_func=lambda raw_parsed_response: raw_parsed_response["results"],

    drop_headers=drop_headers_gsp_substation,
    exclusions={"name": {"TILBURY SGTs 1&7" , "TILBURY SGTs 2&8", "HURST (SPN)"}},
    additional_columns={"type", "external_identifier"},

    name_alias="gsp",
    type_alias="sitetype",
    external_identifier="name",

    primary_alias="Primary Substation",
    bsp_alias="Grid Substation",

    row_transformation_external_identifier=lambda row: row["name"],
    row_transformation_geolocation=lambda row: GEOSPoint(
        row["geo_point_2d"]["lon"], 
        row["geo_point_2d"]["lat"], 
        srid=4326,
    ),
    row_transformation_name=lambda row: normalise_name_and_extract_voltage_info(row.get("name", ""))[0],
    row_transformation_type=lambda row: "gsp",

)


ukpn_gsp_substation_data_resource = DataResource(
    reference="ukpn_substation_gsp",
    base_url=base_url_ukpn,
    dno_group="ukpn",
    data_category="substation",
    path="/api/explore/v2.1/catalog/datasets/ukpn-grid-supply-points-overview/records",
    query_params={"limit": -1},
    headers={"Authorization": f"Apikey {settings.UKPN_API_KEY}"},
    cleaning_helpers=ukpn_gsp_substation_cleaning_helpers,
)


__all__.append("ukpn_gsp_substation_data_resource")
