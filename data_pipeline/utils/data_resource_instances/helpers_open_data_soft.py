import requests
from urllib.parse import urljoin
from django.conf import settings

call_limit_open_data_soft=100

def get_count_open_data_soft(base_url, path, dno_group_abbr, refine: str | None = None):
    """
    Get the total record count from an OpenDataSoft dataset.
    
    Args:
        base_url (str): The Opendatasoft base URL (e.g., https://northernpowergrid.opendatasoft.com)
        path (str): The dataset API path (e.g., /api/explore/v2.1/catalog/datasets/...)
        dno_group_abbr (str): Short DNO group (e.g., "np", "ukpn")
        refine (str, optional): Optional refine query (e.g., "site_purpose:PRIMARY SITE")
    
    Returns:
        int: Total count of matching records.
    """
    api_key_attr = f"{dno_group_abbr.upper()}_API_KEY"
    params = {"limit": 1}
    if refine:
        params["refine"] = refine

    response = requests.get(
        urljoin(base_url, path), 
        params=params,
        headers={"Authorization": f"Apikey {getattr(settings, api_key_attr, None)}"},
        timeout=30,
        )
    response.raise_for_status()
    return response.json()["total_count"]
