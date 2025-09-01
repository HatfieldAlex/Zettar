from django.conf import settings
import pandas as pd 
import requests
from django.contrib.gis.geos import Point as GEOSPoint
from typing import Any, Union, Callable
from ..data_resource_class import DataResource
from .shared_helpers import normalise_name_and_extract_voltage_info, substation_type_map
from ...models import RawFetchedDataStorage
import json
from ..data_resource_class._prepare import _CleaningHelpers
from urllib.parse import urljoin
from .helpers_open_data_soft import get_count_open_data_soft, call_limit_open_data_soft

__all__ = []

drop_headers_primary_bsp_substation = {
    "initial": {
        "town_name", "dno_area", "kva_rating", "easting", "northing",
        "power_on_location_alias", "heat_map_id"
    },
    "subsequent": {"site_name", "site_purpose", "latlong"},
}


np_primary_bsp_substation_cleaning_helpers = _CleaningHelpers(
    extract_payload_func=lambda raw_parsed_response: raw_parsed_response["results"],
    drop_headers=drop_headers_primary_bsp_substation,
    exclusions={"site_purpose": {"GM SECONDARY SITE", "PM SECONDARY SITE"}},

    construct_external_identifier=lambda row: f"{row['asset_id']} (asset id)",
    construct_geolocation=lambda row: GEOSPoint(
        row["latlong"]["lon"], 
        row["latlong"]["lat"], 
        srid=4326
        ),
    construct_name=lambda row: normalise_name_and_extract_voltage_info(row.get("site_name", ""))[0],
    construct_type=lambda row: substation_type_map("PRIMARY SITE", "BULK SUPPLY POINT").get(row["site_purpose"], "unknown"), 
)


base_url_np = "https://northernpowergrid.opendatasoft.com"
path_np_primary_bsp="/api/explore/v2.1/catalog/datasets/substation_sites_list/records"


def create_data_resource(offset, refine_query_parameter):
    return DataResource(
        reference=f"np_substation_primary_bsp_{offset}_{offset + 100}",
        base_url=base_url_np,
        dno_group="np",
        data_category="substation",
        path=path_np_primary_bsp,
        query_params={
            "limit": 100,
            "offset": offset,
            "order_by": "site_name",
            "refine": refine_query_parameter,
        },
        headers={"Authorization": f"Apikey {settings.NP_API_KEY}"},
        cleaning_helpers=np_primary_bsp_substation_cleaning_helpers,
        parse_raw_response_func=lambda raw_resp: raw_resp.json()
    )

#handling primary substations
refine_query_parameter_primary = "site_purpose:PRIMARY SITE"

primary_count = get_count_open_data_soft(base_url_np, path_np_primary_bsp, "np", refine_query_parameter_primary)

for offset in range(0, primary_count, call_limit_open_data_soft):
    data_resource_name = f"np_primary_substation_data_resource_{offset}_{min(offset + call_limit_open_data_soft, primary_count)}"
    globals()[data_resource_name] = create_data_resource(offset, refine_query_parameter_primary)
    __all__.append(data_resource_name)

#handling BSP first
refine_query_parameter_bsp = "site_purpose:BULK SUPPLY POINT"

bsp_count = get_count_open_data_soft(base_url_np, path_np_primary_bsp, "np", refine_query_parameter_bsp)

for offset in range(0, bsp_count, call_limit_open_data_soft):
    data_resource_name = f"np_primary_substation_data_resource_{offset}_{min(offset + call_limit_open_data_soft, bsp_count)}"
    globals()[data_resource_name] = create_data_resource(offset, refine_query_parameter_bsp)
    __all__.append(data_resource_name)

#handling GSPs

drop_headers_gsp_substation = {
    "initial": {
        "licence_area", "voltage_level", "scenario_name", "latitude", "longitude",
        "easting", "northing", "postcode", "year", "number_of_electric_cars_and_vans_hybrid_and_full_electric",
        "number_of_heat_pumps_total", "peak_utilisation_percent_whole_number", 
        "peak_utilisation_with_tout_percent_whole_number",
        "total_installed_non_renewable_generation_capacity_mw", "total_installed_pv_capacity_domestic_mw",
        "total_installed_pv_capacity_i_c_and_large_mw", "total_installed_renewable_generation_capacity_mw",
        "total_installed_storage_capacity_mw", "total_installed_wind_capacity_mw",
        "total_peak_demand_mw", "total_peak_demand_with_tout_mw",
        "domestic_gwh", "domestic_storage_installed_capacity_mw",
        "electric_hgvs_buses_road_vehicles_other_than_vans_cars_and_motorbikes",
        "electrolysers_mwh", "ev_cars_vans_gwh", "ev_other_transport_gwh",
        "hps_domestic_gwh", "hps_i_c_gwh", "i_c_gwh", "i_c_storage_capacity_mw",
        "large_industry_mwh", "number_of_domestic_customers",
        "number_of_domestic_full_electric_heat_pumps", "number_of_domestic_heat_pumps",
        "number_of_domestic_hybrid_heat_pumps", "number_of_electric_buses",
        "number_of_electric_cars_hybrid_and_full_electric",
        "number_of_electric_hgvs", "number_of_electric_vans_hybrid_and_full_electric",
        "number_of_full_electric_cars_and_vans", "number_of_hybrid_electric_cars_and_vans",
        "number_of_i_c_customers", "number_of_i_c_full_electric_heat_pumps",
        "number_of_i_c_heat_pumps", "number_of_i_c_hybrid_heat_pumps",
        "total_baseline_demand_consumption_gwh", "total_demand_gwh",
        "total_installed_biomass_capacity_mw", "total_installed_generation_capacity_mw",
        "total_installed_hydro_capacity_mw", "total_installed_large_mini_chp_capacity_mw",
        "total_installed_other_non_renewable_capacity_mw", "total_installed_renewable_engine_capacity_mw",
        "total_installed_waste_incineration_capacity_mw",
    },   
    "subsequent": {
        "substation", "geopoint"
    },
}

np_gsp_substation_cleaning_helpers = _CleaningHelpers(
    extract_payload_func=lambda raw_parsed_response: raw_parsed_response["results"],
    drop_headers=drop_headers_gsp_substation,

    construct_external_identifier=lambda row: row["substation"],
    construct_geolocation=lambda row: GEOSPoint(
        row["geopoint"]["lon"], 
        row["geopoint"]["lat"], 
        srid=4326,
    ),
    construct_name=lambda row: normalise_name_and_extract_voltage_info(row.get("substation", ""))[0],
    construct_type=lambda row: "gsp",

)



np_gsp_substation_data_resource = DataResource(
    reference="np_substation_gsp",
    base_url=base_url_np,
    dno_group="np",
    data_category="substation",
    path="/api/explore/v2.1/catalog/datasets/northern-powergrid-dfes-gsp-portalformat/records",
    query_params={
        "limit": call_limit_open_data_soft,
        "refine": [
            "year:2023",
            "scenario_name:NG FES - Counterfactual"
        ]
    },
    headers={"Authorization": f"Apikey {settings.NP_API_KEY}"},
    cleaning_helpers=np_gsp_substation_cleaning_helpers,
)


__all__.append("np_gsp_substation_data_resource")
