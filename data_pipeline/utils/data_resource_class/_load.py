from django.core.exceptions import ObjectDoesNotExist
from data_pipeline.models import (
    SubstationCleanedDataStorage, 
    ConnectionApplicationCleanedDataStorage,
)
from location_input.models import DNOGroup, ConnectionVoltageLevel, Substation 


class _DataResourceLoad:
    def load(self, stdout=None, style=None) -> None:
        self._stdout = stdout
        self._style = style
        action = "load"
        self.stage_status_banner(action, "started")

        data_category = self.data_category
        if data_category == "substation":
            self.load_clean_substation_data(action)

        elif data_category == "connection_application":
            self.load_clean_connection_application_data()

        self.stage_status_banner(action, "finished")

    def load_clean_substation_data(self, action) -> None:
        process_success_identifiers = []
        process_failure_identifiers = []
        

        self.log(f"Iterating over cleaned {self.dno_group.upper()} substation records and persisting into core database models...")
        substation_cleaned_data_storage_objs = SubstationCleanedDataStorage.objects.filter(dno_group=self.dno_group)
        count = substation_cleaned_data_storage_objs.count()
        if count == 0:
            self.log("No cleaned substation records found to load.", style_category="warning")
            return
        tally=0
        update_freq_amount = max(1, count // 10) 

        for substation_cleaned_data_storage_obj in substation_cleaned_data_storage_objs:
            name = substation_cleaned_data_storage_obj.name
            type_ = substation_cleaned_data_storage_obj.type
            candidate_voltage_levels_kv = substation_cleaned_data_storage_obj.candidate_voltage_levels_kv
            geolocation = substation_cleaned_data_storage_obj.geolocation
            dno_group = substation_cleaned_data_storage_obj.dno_group
            external_identifier = substation_cleaned_data_storage_obj.external_identifier

            try:
                dno_group_obj = DNOGroup.objects.get(abbr=dno_group)
                connection_voltage_levels_objs = ConnectionVoltageLevel.objects.filter(
                    level_kv__in=candidate_voltage_levels_kv
                )

                substation = Substation.objects.create(
                    name=name,
                    geolocation=geolocation,
                    type=type_,
                    dno_group=dno_group_obj,
                )
                substation.voltage_kv.set(connection_voltage_levels_objs)
                substation.save()

                process_success_identifiers.append(external_identifier)
            
            except ObjectDoesNotExist as e:
                process_failure_identifiers.append(external_identifier)
                self.log(f"Load failed for external identifier {external_identifier}: {e}", style_category="error")

            except Exception as e:
                process_failure_identifiers.append(external_identifier)
                self.log(f"Unexpected load failure for external identifier {external_identifier}: {e}", style_category="error")

            tally+=1

            if tally % update_freq_amount == 0 or tally == count:
                self.log(
                    f"Attempted {tally} / {count} rows... (successful: {len(process_success_identifiers)}, failed: {len(process_failure_identifiers)})")

        if process_failure_identifiers:
            self.log(f"{len(process_success_identifiers)}/{count} rows processed succesfully")
            self.log(f"the following rows failed to process (external_identifiers): {process_failure_identifiers}",
            style_category="warning")
        else:
            self.log(f"All cleaned rows successfully processed", style_category="success",)
            self.stage_status_message(action, "completed successfully", style_category="success")
        
                    


    def load_clean_connection_application_data(self):
        pass