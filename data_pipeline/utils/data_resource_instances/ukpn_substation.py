from django.conf import settings
import pandas as pd 
from django.contrib.gis.geos import Point as GEOSPoint
from typing import Any, Union, Callable
from ..data_resource_class import DataResource
from .shared_helpers import normalise_name_and_extract_voltage_info
from ...models import RawFetchedDataStorage
import json
from ..data_resource_class._prepare import _CleaningHelpers


def extract_payload_ukpn_substation(raw_response):
    return raw_response.json()["results"]


def row_transformation_external_identifier_ukpn_primary_bsp_substation(row):
    return f"{row['name']} | {row['external_identifier']}"

def row_transformation_geolocation_ukpn_primary_bsp_substation(row):
    return GEOSPoint(
            row["spatial_coordinates"]["lon"], 
            row["spatial_coordinates"]["lat"], 
            srid=4326
        )

def row_transformation_name_ukpn_primary_bsp_substation(row):
    return normalise_name_and_extract_voltage_info(row.get("name", ""))[0]

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
    drop_headers=drop_headers_primary_bsp_substation,
    exclusions={},
    additional_columns={},

    name_alias="sitename",
    type_alias="sitetype",
    external_identifier="what3words",

    primary_alias="Primary Substation",
    bsp_alias="Grid Substation",
    gsp_alias="",

    row_transformation_external_identifier=row_transformation_external_identifier_ukpn_primary_bsp_substation,
    row_transformation_geolocation=row_transformation_geolocation_ukpn_primary_bsp_substation,
    row_transformation_name=row_transformation_name_ukpn_primary_bsp_substation,
)


ukpn_primary_bsp_substation_data_resource = DataResource(
    reference="ukpn_substation_primary_bsp",
    base_url="https://ukpowernetworks.opendatasoft.com",
    dno_group="ukpn",
    data_category="substation",
    path="/api/explore/v2.1/catalog/datasets/grid-and-primary-sites/records",
    query_params={
        "limit": -1,
    },
    headers={"Authorization": f"Apikey {settings.UKPN_API_KEY}"},
    cleaning_helpers=ukpn_primary_bsp_substation_cleaning_helpers,
    extract_payload_func=extract_payload_ukpn_substation,
)



#----------------------

def row_transformation_external_identifier_gsp_substation(row):
    return row["gsp"]

def row_transformation_geolocation_gsp_substation(row):
    return GEOSPoint(
            row["geo_point_2d"]["lon"], 
            row["geo_point_2d"]["lat"], 
            srid=4326
        )

def row_transformation_name_ukpn_gsp_substation(row):
    return normalise_name_and_extract_voltage_info(row.get("name", ""))[0]

def row_transformation_type_ukpn_gsp_substation(row):
    return "gsp"

def row_transformation_external_identifier_ukpn_gsp_substation(row):
    return row["name"]

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
    drop_headers=drop_headers_gsp_substation,
    exclusions={"name": {"TILBURY SGTs 1&7" , "TILBURY SGTs 2&8", "HURST (SPN)"}},
    additional_columns={"type", "external_identifier"},

    name_alias="gsp",
    type_alias="sitetype",
    external_identifier="name",

    primary_alias="Primary Substation",
    bsp_alias="Grid Substation",

    row_transformation_external_identifier=row_transformation_external_identifier_ukpn_gsp_substation,
    row_transformation_geolocation=row_transformation_geolocation_gsp_substation,
    row_transformation_name=row_transformation_name_ukpn_gsp_substation,
    row_transformation_type=row_transformation_type_ukpn_gsp_substation,
)


ukpn_gsp_substation_data_resource = DataResource(
    reference="ukpn_substation_gsp",
    base_url="https://ukpowernetworks.opendatasoft.com",
    dno_group="ukpn",
    data_category="substation",
    path="/api/explore/v2.1/catalog/datasets/ukpn-grid-supply-points-overview/records",
    query_params={
        "limit": -1,
    },
    headers={"Authorization": f"Apikey {settings.UKPN_API_KEY}"},
    cleaning_helpers=ukpn_gsp_substation_cleaning_helpers,
    extract_payload_func=extract_payload_ukpn_substation,
)





__all__ = ["ukpn_primary_bsp_substation_data_resource", "ukpn_gsp_substation_data_resource"]
