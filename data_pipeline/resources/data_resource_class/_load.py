from dataclasses import dataclass, field

import pandas as pd 

from core.models import DNOGroup, Substation
from data_pipeline.models import SubstationCleanedDataStorage
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction


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
        cleaned_data_qs = SubstationCleanedDataStorage.objects.filter(reference=self.reference)
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
                with transaction.atomic():
                    self._remove_existing_substation(cleaned_data_storage_instance)
                    self._create_substation(cleaned_data_storage_instance, dno_group_obj)
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
        self._log_load_outcomes(count, load_summary_process_failure_identifiers, action)
        
    def _create_substation(self, substation_cleaned_data_storage_obj, dno_group_obj):
        substation = Substation.objects.create(
            name=substation_cleaned_data_storage_obj.name,
            geolocation=substation_cleaned_data_storage_obj.geolocation,
            type=substation_cleaned_data_storage_obj.type,
            dno_group=dno_group_obj,
            external_identifier=substation_cleaned_data_storage_obj.external_identifier,
            )
        substation.save()
        
    def _remove_existing_substation(self, substation_cleaned_data_storage_obj):
        Substation.objects.filter(
            external_identifier=substation_cleaned_data_storage_obj.external_identifier
            ).delete()
      
    def _log_load_outcomes(self, count, load_summary_process_failure_identifiers, action):

        if load_summary_process_failure_identifiers:
            self.log(f"{len(self._load_summary.process_success_identifiers)}/{count} rows processed succesfully")
            self.log(f"the following rows failed to process (external_identifiers): {load_summary_process_failure_identifiers}",
            style_category="warning")
        else:
            self.log(f"All cleaned rows successfully processed", style_category="success",)
            
        if not load_summary_process_failure_identifiers:
            self.stage_status_message(action, "completed successfully", style_category="success")

        self.stage_status_banner(action, "finished")