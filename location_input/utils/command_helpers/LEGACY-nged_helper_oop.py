from zettar_prototype.location_input.utils.command_helpers_refactor.helper_functions_oop import DNO, DataResource, ResourceCleaner
from django.conf import settings
from settings import NGED_API_KEY 


nged_substation_cleaner = ResourceCleaner()

nged_substation_data_resource = DataResource(
    base_url="https://connecteddata.nationalgrid.co.uk/api/3/action",
    path="datastore_search",
    query_params={
        "resource_id": "e06413f8-0d86-4a13-b5c5-db14829940ed", 
        "fields": "Substation Number,Substation Name,Substation Type,Latitude,Longitude",
        "limit": 3000,
        },
    headers={"Authorization": f"{NGED_API_KEY}"},
    resource_cleaner=nged_substation_cleaner,
)

nged_substation_data_resource.fetch_data_resource()
print(nged_substation_data_resource.raw_data)


