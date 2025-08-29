from django.conf import settings
import pandas as pd 
from django.contrib.gis.geos import Point as GEOSPoint
from typing import Any, Union, Callable
from ..data_resource_class import DataResource
from .shared_helpers import normalise_name_and_extract_voltage_info
from ...models import RawFetchedDataStorage
import json

ukpn_field_type_aliases_map = {
        "Primary Substation": "primary",
        "Grid Substation": "bsp",
    }

ukpn_headers_rename_map = {
        "what3words": "external_identifier",
        "sitename": "name",
        "sitetype": "type",
    }

drop_types = {}

drop_headers = {
    "sitefunctionallocation", "licencearea", "sitevoltage", "esqcroverallrisk", "gridref", 	
    "siteassetcount", "powertransformercount", "electricalassetcount", "civilassetcount", 
    "street", "suburb", "towncity", "county", "postcode",	"yearcommissioned", "datecommissioned",	
    "siteclassification", "assessmentdate", "last_report", "calculatedresistance", "northing",	
    "measuredresistance_ohm", "next_assessmentdate", "easting",  "transratingwinter",
    "transratingsummer", "reversepower", "maxdemandsummer", "maxdemandwinter",	
    "local_authority", "local_authority_code"
}

def extract_payload_ukpn_substation(raw_response):
    return raw_response.json()["results"]

def ukpn_substation_clean(
    raw_payload_json: Union[dict[str, Any], list[dict[str, Any]]],
    log: Callable[[str, str], None] = print
    ) -> pd.DataFrame:

    log("Converting raw JSON payload into DataFrame...")
    df = pd.DataFrame.from_records(raw_payload_json)

    log("Dropping columns not required...")
    df.drop(columns=drop_headers, inplace=True)

    log("Filtering out irrelevant data...")
    #empty

    log("Generating 'geolocation' column as GEOS Point objects using longitude and latitude, and dropping the original columns...")
    df["geolocation"] = df.apply(lambda r: GEOSPoint(r["spatial_coordinates"]["lon"], r["spatial_coordinates"]["lat"], srid=4326),axis=1)
    df.drop(columns=["spatial_coordinates"], inplace=True)
    
    log("Renaming headers to align with validation schema...")
    df = df.rename(columns=ukpn_headers_rename_map)

    log("Standardising substation type labels for consistency...")
    df["type"] = df["type"].map(ukpn_field_type_aliases_map)
  
    log("Normalising substation names and extracting voltage level candidates (in kV)...")
    df[["name"]] = df["name"].apply(lambda n: pd.Series(normalise_name_and_extract_voltage_info(n)[0]))
    
    log("Assigning DNO group identifier to each record...")
    df["dno_group"] = "ukpn"
    df["reference"] = "ukpn_substation_primary_bsp"

    log("Implementing the external_identifier...")
    #done

    return df


ukpn_substation_primary_bsp_data_resource = DataResource(
    reference="ukpn_substation_primary_bsp",
    base_url="https://ukpowernetworks.opendatasoft.com",
    dno_group="ukpn",
    data_category="substation",
    path="/api/explore/v2.1/catalog/datasets/grid-and-primary-sites/records",
    query_params={
        "limit": -1,
    },
    headers={"Authorization": f"Apikey {settings.UKPN_API_KEY}"},
    clean_func=ukpn_substation_clean,
    extract_payload_func=extract_payload_ukpn_substation,
)




__all__ = ["ukpn_substation_primary_bsp_data_resource"]