from django.conf import settings
import pandas as pd 
import requests
from django.contrib.gis.geos import Point as GEOSPoint
from typing import Any, Union, Callable
from ..data_resource_class import DataResource
from .utils import normalise_raw_name_entry, substation_type_map, get_count_open_data_soft, call_limit_open_data_soft
from ...models import RawFetchedDataStorage
import json
from ..data_resource_class._prepare import _CleaningHelpers
from urllib.parse import urljoin

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
    "subsequent": {"sitename", "sitetype", "what3words", "spatial_coordinates"}
}

ukpn_primary_bsp_substation_cleaning_helpers = _CleaningHelpers(
    extract_payload_func=lambda raw_parsed_response: raw_parsed_response["results"],
    drop_headers=drop_headers_primary_bsp_substation,

    construct_external_identifier=lambda row: f"{row['sitename']} | {row['what3words']}",
    construct_geolocation=lambda row: GEOSPoint(
        row["spatial_coordinates"]["lat"],
        row["spatial_coordinates"]["lon"], 
        srid=4326
        ),
    construct_name=lambda row: normalise_raw_name_entry(row.get("sitename", "")),
    construct_type=lambda row: substation_type_map("Primary Substation", "Grid Substation").get(row["sitetype"], "unknown"), 
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

count = get_count_open_data_soft(base_url_ukpn, path_ukpn_primary_bsp, "ukpn")

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
        "geo_point_2d", "gsp",
    },
}

ukpn_gsp_substation_cleaning_helpers = _CleaningHelpers(
    extract_payload_func=lambda raw_parsed_response: raw_parsed_response["results"],
    drop_headers=drop_headers_gsp_substation,
    exclusions={"gsp": {"TILBURY SGTs 1&7" , "TILBURY SGTs 2&8", "HURST (SPN)"}},

    construct_external_identifier=lambda row: row["gsp"],
    construct_geolocation=lambda row: GEOSPoint(
        row["geo_point_2d"]["lat"],
        row["geo_point_2d"]["lon"], 
        srid=4326,
    ),
    construct_name=lambda row: normalise_raw_name_entry(row.get("gsp", "")),
    construct_type=lambda row: "gsp",

)


ukpn_gsp_substation_data_resource = DataResource(
    reference="ukpn_substation_gsp",
    base_url=base_url_ukpn,
    dno_group="ukpn",
    data_category="substation",
    path="/api/explore/v2.1/catalog/datasets/ukpn-grid-supply-points-overview/records",
    query_params={"limit": call_limit_open_data_soft},
    headers={"Authorization": f"Apikey {settings.UKPN_API_KEY}"},
    cleaning_helpers=ukpn_gsp_substation_cleaning_helpers,
)


__all__.append("ukpn_gsp_substation_data_resource")
