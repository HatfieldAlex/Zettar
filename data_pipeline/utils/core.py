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

    _stdout: Any = None
    _style: Any = None
    
    @property
    def url(self) -> str:
        """constructs full URL"""
        components = [self.base_url.rstrip("/"), self.path.strip("/"), self.path_parameter.strip("/")]
        return "/".join(c for c in components if c)

    def log(self, msg: str, stdout=None, style=None, style_category="notice") -> None:
        """
        Logs a message to stdout with optional Django styling.
        """
        stdout = stdout or getattr(self, '_stdout', None)
        style = style or getattr(self, '_style', None)
        if stdout:
            if style and style_category:
                try:
                    style_fn = getattr(style, style_category.upper(), None)
                    styled_msg = style_fn(msg) if style_fn else msg
                except Exception:
                    styled_msg = msg
            else:
                styled_msg = msg
            stdout.write(styled_msg + "\n")
        else:
            print(msg)

    def ingest(self, stdout=None, style=None) -> bool:
        success_bool = False
        self._stdout = stdout
        self._style = style
        BOLD = "\033[1m"
        RESET = "\033[0m"

        self.log("=" * 100, stdout, style, "notice")
        self.log(f"{BOLD}[INGESTION STAGE STARTED]{RESET}")
        self.log("-" * 100, stdout, style, "notice")
        self.log(f"Fetching data from {self.url} ...")

        try:
            response = requests.get(
                self.url, 
                params=self.query_params or None, 
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            self.log(f"Data successfully fetched", style_category="success")

            self.log(f"Storing fetched data in {RawFetchedDataStorage._meta.db_table} ...")
            raw_data_storage = RawFetchedDataStorage.objects.create(
                data_category=self.data_category,
                dno_group=self.dno_group,
                source_url=self.url,
                raw_data=response
                )

            if raw_data_storage.id:
                self.log(f"Data successfully stored (id: {raw_data_storage.id})", style_category="success")

                if self.raw_data_storage_id:
                    self.log(f"Deleting previously fetched data (id: {self.raw_data_storage_id}) ...")
                    RawFetchedDataStorage.objects.filter(id=self.raw_data_storage_id).delete()
                    self.log("Previously fetched data deleted")
                    
                self.raw_data_storage_id = raw_data_storage.id
                self.log(f"\n{BOLD}[INGESTION STAGE COMPLETED SUCCESSFULLY]{RESET}", style_category="success")
                success_bool = True    

            else:
                self.log(f"Failed to store data", style_category="error")
        except requests.RequestException as e: 
            self.log(f"Failed to fetch data: {e}", style_category="error")
        
        finally:
            self.log("-" * 100)
            self.log(f"{BOLD}[INGESTION STAGE FINISHED]{RESET}")
            self.log("=" * 100)
            return success_bool


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



