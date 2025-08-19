from dataclasses import dataclass
import pandas as pd
from data_pipeline.models import RawFetchedDataStorage, SubstationCleanedDataStorage, ConnectionApplicationCleanedDataStorage
from .validators import CleanSubstationDataRequirements

class _DataResourcePrepare:
    def prepare(self, stdout=None, style=None) -> None:
        action = "preparation"
        previous_data_storage_ref = self.cleaned_data_storage_ref
        new_cleaned_data_storage_ref = self.raw_data_storage_ref
        self._stdout = stdout
        self._style = style
        self.stage_status_banner(action, "started")

        raw_fetched_data_storage_id, raw_payload_json = self._query_data()
        df = self._clean_data(raw_payload_json, new_cleaned_data_storage_ref)
        valid_cleaned_data_rows = self._validate_cleaned_data(df)
        success_count = self._store_validated_data(valid_cleaned_data_rows, raw_fetched_data_storage_id)
        self._delete_previous_cleaned_data(previous_data_storage_ref, new_cleaned_data_storage_ref)


        if success_count == len(df):
            self.mark_section("-")
            self.stage_status_message(action, "completed successfully", style_category="success")

        self.stage_status_banner(action, "finished")



    def _query_data(self):
        self.log(f"Querying data from {RawFetchedDataStorage._meta.db_table} ...")
        fetched_data_obj = RawFetchedDataStorage.objects.get(id=self.raw_data_storage_ref)
        raw_fetched_data_storage_id = fetched_data_obj.id
        raw_payload_json = fetched_data_obj.raw_payload_json
        return (raw_fetched_data_storage_id, raw_payload_json)

    def _clean_data(self, raw_payload_json, new_cleaned_data_storage_ref):
        self.log(f"Commencing data clean...")
        df = self.clean_func(raw_payload_json, self.log)
        df["reference"] = new_cleaned_data_storage_ref
        self.log(f"Data cleaning completed successfully.", style_category="success")
        return df

    def _validate_cleaned_data(self, df):
        self.log(f"Commencing data validation...")
        cleaned_data_rows = list(df.iterrows())
        valid_cleaned_data_rows = []  
        invalid_cleaned_data_rows = [] 
        total = len(cleaned_data_rows)
        update_freq_amount = max(1, total // 10) 

        for i, row in cleaned_data_rows:
            j = i + 1
            record = row.to_dict()
            try:
                validated = CleanSubstationDataRequirements(**record)
                valid_cleaned_data_rows.append(validated)
            except Exception as e:
                ext_id = record.get("external_identifier") or record.get("_id")
                invalid_cleaned_data_rows.append(ext_id)
                self.log(f"Skipped invalid row (external_identifier={ext_id}): {e}", style_category="warning",)

            if j % update_freq_amount == 0 or j == total:
                self.log(f"Attempted validation of {j}/{total} rows... (successful: {len(valid_cleaned_data_rows)}, failed: {len(invalid_cleaned_data_rows)})")

        if invalid_cleaned_data_rows:
            self.log(
                f"{total} / {len(cleaned_data_rows)} cleaned rows validated successfully.", 
                style_category="warning",
            )
            self.log(
                f"The following rows failed to validate (external_identifiers): {invalid_cleaned_data_rows}",
                style_category="warning",
            )
            return valid_cleaned_data_rows
        else:
            self.log("All cleaned data validated.", style_category="success")
            return valid_cleaned_data_rows

    def _store_validated_data(self, validated_data, raw_fetched_data_storage_id):
        self.log("Storing validated cleaned data...")
        total = len(validated_data)

        if total == 0:
            self.log("No validated data to store.", style_category="warning")


        update_freq_amount = max(1, total // 10) 
        stored_count = 0
        failed_ids = []

        for idx, validated in enumerate(validated_data, start=1):
            try:
                SubstationCleanedDataStorage.objects.create(
                    **validated.model_dump(),
                    raw_data_record_id=raw_fetched_data_storage_id,
                    )
                stored_count += 1
            except Exception as e:
                ext_id = getattr(validated, "external_identifier", None)
                failed_ids.append(ext_id)
                self.log(
                    f"Failed to store row (external_identifier={ext_id}): {e}",
                    style_category="error",
                )

            if idx % update_freq_amount == 0 or idx == total:
                self.log(f"Attempted {idx}/{total} rows... (successful: {stored_count}, failed: {len(failed_ids)})")

        if failed_ids:
            self.log(
                f"{stored_count}/{total} cleaned rows stored successfully.", style_category="warning",)
            self.log(
                f"The following rows failed to store (external_identifiers): {failed_ids}",
                style_category="error",
            )
        else:
            self.log(f"All storage of {total} cleaned rows stored successfully.", style_category="success",)

        return stored_count

    def _delete_previous_cleaned_data(self, previous_data_storage_ref, new_cleaned_data_storage_ref):

        if not previous_data_storage_ref:
            self.cleaned_data_storage_ref = new_cleaned_data_storage_ref
            return

        self.log(f"Deleting previously stored data...")
        SubstationCleanedDataStorage.objects.filter(reference=previous_data_storage_ref).delete()
        self.cleaned_data_storage_ref = new_cleaned_data_storage_ref


