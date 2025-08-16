from .helper_functions_oop import DNO, DataResource, ResourceCleaner

nged_substation_cleaner = ResourceCleaner()

nged_substation_data_resource = DataResource(
    base_url="",
    path="",
    resource_identifier="",
    query_params=,
    request_headers={"Authorization": "Bearer <token>"},
    resource_cleaner=nged_substation_cleaner,

)

