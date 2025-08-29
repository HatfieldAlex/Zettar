from django.core.exceptions import ObjectDoesNotExist
from data_pipeline.models import (
    SubstationCleanedDataStorage, 
    ConnectionApplicationCleanedDataStorage,
)
from location_input.models import DNOGroup, ConnectionVoltageLevel, Substation
from dataclasses import dataclass, field

@dataclass
class _LoadSummary:
    process_success_identifiers: list = field(default_factory=list) 
    process_failure_identifiers: list = field(default_factory=list) 


class _DataResourceLoad:
    def load(self, stdout=None, style=None) -> None:
        self._stdout = stdout
        self._style = style
        action = "load"
        self.stage_status_banner(action, "started")

        self._load_summary = _LoadSummary()
        data_category = self.data_category
        dno_group = self.dno_group
        dno_group_obj = DNOGroup.objects.get(abbr=dno_group)
        cleaned_data_storage_model = self._load_map(data_category, "cleaned_data_storage_model")
        persist = self._load_map(data_category, "persistence_fn")
        cleaned_data_qs = cleaned_data_storage_model.objects.filter(reference=self.reference)
        cleaned_data_objs = list(cleaned_data_qs)
        count = len(cleaned_data_objs)
        
        self.log(f"Iterating over cleaned {self.reference.replace("_", " ")} records and persisting into core database models...")
        if count == 0:
            self.log(f"No cleaned {self.reference.replace("_", " ")} records found to load.", style_category="warning")
            self.stage_status_banner(action, "finished")
            return

        tally=0
        update_freq_amount = max(1, count // 10) 

        for cleaned_data_storage_instance in cleaned_data_qs:
            external_identifier = cleaned_data_storage_instance.external_identifier

            try:
                persist(cleaned_data_storage_instance, dno_group_obj)
                self._load_summary.process_success_identifiers.append(external_identifier)
            except ObjectDoesNotExist as e:
                self._load_summary.process_failure_identifiers.append(external_identifier)
                self.log(f"Load failed for external identifier {external_identifier}: {e}", style_category="error")
            except Exception as e:
                self._load_summary.process_failure_identifiers.append(external_identifier)
                self.log(f"Unexpected load failure for external identifier {external_identifier}: {e}", style_category="error")

            tally+=1
            if tally % update_freq_amount == 0 or tally == count:
                self.log(
                    f"Attempted {tally} / {count} rows... (successful: {len(self._load_summary.process_success_identifiers)}, failed: {len(self._load_summary.process_failure_identifiers)})")




        load_summary_process_failure_identifiers = self._load_summary.process_failure_identifiers

        if load_summary_process_failure_identifiers:
            self.log(f"{len(self._load_summary.process_success_identifiers)}/{count} rows processed succesfully")
            self.log(f"the following rows failed to process (external_identifiers): {load_summary_process_failure_identifiers}",
            style_category="warning")
        else:
            self.log(f"All cleaned rows successfully processed", style_category="success",)
            


        if cleaned_data_objs:  
            self.log("Deleting previously loaded data...")       
            for obj in cleaned_data_objs:
                obj.delete()
            self.log("All previously loaded data deleted...")

        if not load_summary_process_failure_identifiers:
            self.stage_status_message(action, "completed successfully", style_category="success")

        self.stage_status_banner(action, "finished")

    def _load_map(self, data_category, key):
        handlers = {
            "substation": {
                "cleaned_data_storage_model": SubstationCleanedDataStorage,
                "persistence_fn": self._create_substation
            },
            "connection_application": {
                "cleaned_data_storage_model": ConnectionApplicationCleanedDataStorage,
                "persistence_fn": self._create_connection_application
            }
        }

        try:
            return handlers[data_category][key]
        except KeyError:
            raise ValueError(f"Invalid data_category '{data_category}' or key '{key}' in handler map.")
        
    def _create_substation(self, substation_cleaned_data_storage_obj, dno_group_obj):
        substation = Substation.objects.create(
            name=substation_cleaned_data_storage_obj.name,
            geolocation=substation_cleaned_data_storage_obj.geolocation,
            type=substation_cleaned_data_storage_obj.type,
            dno_group=dno_group_obj
            )
        connection_voltage_levels_objs = ConnectionVoltageLevel.objects.filter(
            level_kv__in=substation_cleaned_data_storage_obj.candidate_voltage_levels_kv
        )
        substation.voltage_kv.set(connection_voltage_levels_objs)

        substation.save()
        
    def _create_connection_application(self, connection_application_cleaned_data_storage_obj, dno_group_obj):
        obj = connection_application_cleaned_data_storage_obj
        new_connection = NewConnection.objects.create(
            connection_status = obj.connection_status
            connection_voltage_level = obj.connection_voltage_level 
            dno_group = dno_group_obj
            demand_count = obj.demand_count
            total_demand_capacity_mw = obj.total_demand_capacity_mw
            generation_count = obj.generation_count
            total_generation_capacity_mw = obj.total_generation_capacity_mw
        )
