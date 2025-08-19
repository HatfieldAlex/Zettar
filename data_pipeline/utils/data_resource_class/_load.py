from dataclasses import dataclass
from data_pipeline.models import (
    RawFetchedDataStorage,
    SubstationCleanedDataStorage, 
    ConnectionApplicationCleanedDataStorage,
)
from .validators import CleanSubstationDataRequirements
from ...models import SubstationCleanedDataStorage




class _DataResourceLoad:
    def load(self) -> None:
        data_category = self.data_category
        if data_category == "substation":
            for cleaned_record in SubstationCleanedDataStorage.objects.filter(dno_group=self.dno_group):
                self.load_clean_substation_data(cleaned_record)

        elif data_category == "connection_application":
            for cleaned_record in ConnectionApplicationCleanedDataStorage.objects.filter(dno_group=self.dno_group):
                self.load_clean_connection_application_data(cleaned_record)

    def load_clean_substation_data(record: SubstationCleanedDataStorage):
        name = record.name
        type = record.type
        candidate_voltage_levels_kv = record.candidate_voltage_levels_kv
        geolocation = record.geolocation
        dno_group = record.dno_group
        

        dno_group_obj = DNOGroup.objects.get(abbr=dno_group)
        connection_voltage_levels_objs = ConnectionVoltageLevel.objects.filter(
            level_kv__in=candidate_voltage_levels_kv
        )

        substation = Substation.objects.create(
            name=name,
            geolocation=geolocation,
            type=type,
            dno_group=dno_group_obj,
        )
        substation.voltage_kv.set(connection_voltage_levels_objs)
        substation.save()

    def load_clean_connection_application_data(record: SubstationCleanedDataStorage):
        pass