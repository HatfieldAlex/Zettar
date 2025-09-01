import requests
from urllib.parse import urljoin
from django.conf import settings

call_limit_open_data_soft=100

def get_count_open_data_soft(base_url, path):
    response = requests.get(
        urljoin(base_url, path), 
        params={"limit": 1},
        headers={"Authorization": f"Apikey {settings.UKPN_API_KEY}"},
        timeout=30,
        )
    response.raise_for_status()
    return response.json()["total_count"]
