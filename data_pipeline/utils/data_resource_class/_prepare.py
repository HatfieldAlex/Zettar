from dataclasses import dataclass
import pandas as pd
from data_pipeline.models import RawFetchedDataStorage, SubstationCleanedDataStorage, ConnectionApplicationCleanedDataStorage
from .validators import CleanSubstationDataRequirements

class _DataResourcePrepare:
    def prepare(self, stdout=None, style=None) -> bool:
        success_bool = False
        self._stdout = stdout
        self._style = style

        self.stage_status_banner("preparation", "started")

        self.log(f"Querying data from {RawFetchedDataStorage._meta.db_table} ...")
        fetched_data_obj = RawFetchedDataStorage.objects.get(id=self.raw_data_storage_id)
        raw_response = fetched_data_obj.raw_response

        self.log(f"Cleaning data ...")
        df = self.clean_func(raw_response)
        self.log(f"Data cleaning completed successfully.", style_category="success")

        for _, row in df.iterrows():
            print(row)
            record = row.to_dict()
            try:
                validated = CleanSubstationDataRequirements(**record)
                SubstationCleanedDataStorage.objects.create(**validated.model_dump())
            except Exception as e:
                print(f"skipped invalid row: {e}")