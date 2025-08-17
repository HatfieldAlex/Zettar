from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Optional, Literal
from dataclasses import dataclass, field
from typing import Any, Mapping, Union
from shapely.geometry import Point
import pandas as pd
import requests
from django.conf import settings
from data_pipeline.models import RawDataRecord



@dataclass(slots=True)
class DataResource:
    _registry: ClassVar[list["DataResource"]] = [] 

    base_url: str
    dno: Literal["nged"]
    data_category: Literal["substations", "connection_applications"]
    path: str = ""
    path_parameter: str = ""
    query_params: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    timeout: float = 30.0
    clean_func: Callable[[dict[str, Any] | list[Any]], pd.DataFrame] | None = None
    

    @property
    def url(self) -> str:
        """constructs full URL"""
        components = [self.base_url.rstrip("/"), self.path.strip("/"), self.path_parameter.strip("/")]
        return "/".join(c for c in components if c)

    def fetch_data_resource(self) -> None:
        response = requests.get(
            self.url, 
            params=self.query_params or None, 
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()

        raw_data = response.json() if "json" in (response.headers.get("content-type") or "").lower() else response.text

        RawDataRecord.objects.create(
            data_category=self.data_category,
            dno_group=self.dno,
            source_url=self.url,
            raw_data=raw_data
            )

        
    def clean(self) -> None:
        pass
        # if df.validate:
        #     pass
        #     # self.cleaned_data = df
        # else:
        #     pass
        #     #some error
    
    def process(self) -> None:
        pass

    def __post_init__(self):
        self.__class__._registry.append(self)

    @classmethod
    def filter(cls, *, dno: str = None, data_category: str = None):
        return [
        r for r in cls._registry
        if (dno is None or r.dno == dno) and
           (data_category is None or r.data_category == data_category)
    ]



