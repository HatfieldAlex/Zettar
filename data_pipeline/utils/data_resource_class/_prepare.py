from dataclasses import dataclass
import pandas as pd
from data_pipeline.models import RawFetchedDataStorage, SubstationCleanedDataStorage, ConnectionApplicationCleanedDataStorage
from .validators import CleanSubstationDataRequirements

class _DataResourcePrepare:
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