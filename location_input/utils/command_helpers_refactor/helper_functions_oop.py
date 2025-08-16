from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Optional
from dataclasses import dataclass, field
from typing import Any, Mapping, Union
import pandas as pd
import requests


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
    resource_identifier: str = ""

    @property
    def url(self) -> str:
        """constructs full URL"""
        components = [self.base_url.rstrip("/"), self.path.strip("/"), self.resource_identifier.strip("/")]
        return "/".join(c for c in components if c)

    query_params: dict[str, str] = field(default_factory=dict)
    
    additional_headers: dict[str, str] = field(default_factory=dict)
    timeout: float = 30.0

    raw_data: JSON | None = None
    cleaned_data: pd.DataFrame | None = None 


    def fetch_data_resource(self) -> None:
        response = requests.get(
            self.url, 
            params=self.query_params or None, 
            headers=headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        self.raw_data = response.json() if "json" in (response.headers.get("content-type"), or "") else response.text

    def clean_fetched_data(self) -> None:
        cleaner_helpers=self.resource_cleaner
        #get dataframe object
        self.cleaned_data_dataframe = dataframe obj
    
    def save_data(self) -> None:
        #save to application database
        clenaed_dataframe = self.clenaed_dataframe
        cleaned_data_location.add(cleaned_dataframe)






@dataclass(frozen=True, slots=True)
class DNO:
    name: str
    substation_data_resources: tuple[DataResource] = field(default_factory=tuple)
    connection_application_data_resources: tuple[DataResource] = field(default_factory=tuple)
