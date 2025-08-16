from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Optional
from dataclasses import dataclass, field
from typing import Any, Mapping, Union
import pandas as pd
import requests
from django.conf import settings


@dataclass
class ResourceCleaner:
    pass 
    #this will includ eeverthing needed to clean the given dataclass


@dataclass(slots=True)
class DataResource:
    #endpoint
    base_url: str
    resource_cleaner: ResourceCleaner

    path: str = ""
    path_parameter: str = ""

    raw_data: Union[dict[str, Any], list[Any]] | None = None
    cleaned_data: pd.DataFrame | None = None 

    @property
    def url(self) -> str:
        """constructs full URL"""
        components = [self.base_url.rstrip("/"), self.path.strip("/"), self.path_parameter.strip("/")]
        return "/".join(c for c in components if c)

    query_params: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    timeout: float = 30.0



    def fetch_data_resource(self) -> None:
        response = requests.get(
            self.url, 
            params=self.query_params or None, 
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        self.raw_data = response.json() if "json" in (response.headers.get("content-type") or "").lower() else response.text

    def clean_fetched_data(self) -> None:
        pass
        # cleaner_helpers=self.resource_cleaner
        # #get dataframe object
        # self.cleaned_data_dataframe = dataframe obj
    
    def save_data(self) -> None:
        pass
        # #save to application database
        # clenaed_dataframe = self.clenaed_dataframe
        # cleaned_data_location.add(cleaned_dataframe)






@dataclass(frozen=True, slots=True)
class DNO:
    name: str
    substation_data_resources: tuple[DataResource] = field(default_factory=tuple)
    connection_application_data_resources: tuple[DataResource] = field(default_factory=tuple)

