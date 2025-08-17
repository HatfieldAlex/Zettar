from __future__ import annotations

from dataclasses import dataclass, field
import requests
from typing import Any, Callable, ClassVar, Literal, Mapping, Optional, Union

import pandas as pd
from shapely.geometry import Point

from django.conf import settings

from data_pipeline.models import (
    RawFetchedDataStorage,
    SubstationCleanedDataStorage, 
    ConnectionApplicationCleanedDataStorage,
)
from .shared_helpers import (
    load_clean_connection_application_data,
    load_clean_substation_data,
)
from .validators import CleanSubstationDataRequirements  


@dataclass(slots=True)
class DataResource:
    _registry: ClassVar[list["DataResource"]] = [] 

    base_url: str
    dno_group: Literal["nged"]
    data_category: Literal["substation", "connection_application"]
    path: str = ""
    path_parameter: str = ""
    query_params: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    timeout: float = 30.0

    clean_func: Callable[[dict[str, Any] | list[Any]], pd.DataFrame] | None = None
    raw_data_storage_id: int | None = None
    
    @property
    def url(self) -> str:
        """constructs full URL"""
        components = [self.base_url.rstrip("/"), self.path.strip("/"), self.path_parameter.strip("/")]
        return "/".join(c for c in components if c)


    def ingest(self) -> None:
        response = requests.get(
            self.url, 
            params=self.query_params or None, 
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()

        raw_data_storage = RawFetchedDataStorage.objects.create(
            data_category=self.data_category,
            dno_group=self.dno_group,
            source_url=self.url,
            raw_data=response
            )

        if self.raw_data_storage_id is None:
            raise ValueError("No raw data has been ingested yet.")

        self.raw_data_storage_id = raw_data_storage.id

    def prepare(self) -> None:
        fetched_data = RawFetchedDataStorage.objects.get(id=self.raw_data_storage_id)
        df = self.clean_func(fetched_data)

        for _, row in df.iterrows():
            record = row.to_dict()
            try:
                validated = CleanSubstationDataRequirements(**record)
                SubstationCleanedDataStorage.objects.create(**validated.model_dump())
            except Exception as e:
                print(f"skipped invalid row: {e}")
    
    def load(self) -> None:
        data_category = self.data_category
        if data_category == "substation":
            for cleaned_record in SubstationCleanedDataStorage.objects.filter(dno_group=self.dno_group):
                load_clean_substation_data(cleaned_record)

        elif data_category == "connection_application":
            for cleaned_record in ConnectionApplicationCleanedDataStorage.objects.filter(dno_group=self.dno_group):
                load_clean_connection_application_data(cleaned_record)


    def __post_init__(self):
        self.__class__._registry.append(self)

    @classmethod
    def filter(cls, *, dno_group: str = None, data_category: str = None):
        return [
        r for r in cls._registry
        if (dno_group is None or r.dno_group == dno_group) and
           (data_category is None or r.data_category == data_category)
    ]



