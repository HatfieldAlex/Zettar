from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, ClassVar, Literal
import pandas as pd
import requests


@dataclass(slots=True)
class _DataResourceBase:
    _registry: ClassVar[list["DataResource"]] = [] 

    reference: str
    
    base_url: str
    dno_group: Literal["nged"]
    data_category: Literal["substation", "connection_application"]
    path: str = ""
    path_parameter: str = ""
    query_params: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    timeout: float = 30.0

    
    clean_func: Callable[..., pd.DataFrame] | None = None
    extract_payload_func: Callable[[requests.Response], Any] = lambda resp: resp.json()

    

    _stdout: Any = None
    _style: Any = None
    
    @property
    def url(self) -> str:
        """constructs full URL"""
        components = [self.base_url.rstrip("/"), self.path.strip("/"), self.path_parameter.strip("/")]
        return "/".join(c for c in components if c)
        
    def __post_init__(self):
        self.__class__._registry.append(self)

    @classmethod
    def filter(cls, *, dno_group: str = None, data_category: str = None):
        return [
        r for r in cls._registry
        if (dno_group is None or r.dno_group == dno_group) and
           (data_category is None or r.data_category == data_category)
    ]