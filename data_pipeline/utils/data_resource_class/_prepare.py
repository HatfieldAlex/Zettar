from dataclasses import dataclass, field
import pandas as pd
from data_pipeline.models import RawFetchedDataStorage, SubstationCleanedDataStorage, ConnectionApplicationCleanedDataStorage
from .validators import CleanSubstationDataRequirement, CleanConnectionApplicationDataRequirement
from django.utils.timezone import now

@dataclass
class _PrepareSummary:
    total_cleaned_data_rows: int = 0

    valid_cleaned_data_rows: list = field(default_factory=list) 
    invalid_cleaned_data_rows: list = field(default_factory=list) 
    total_valid_data_rows: int | None = None

    successful_storage_valid_cleaned_data_rows: list = field(default_factory=list)
    failed_storage_valid_cleaned_data_rows: list = field(default_factory=list) 
    total_stored_valid_data_rows: int = 0

    def update_freq_amount(self, total):
        return max(1, total // 10) 


class _DataResourcePrepare:    
    def prepare(self, stdout=None, style=None) -> None:
        action = "preparation"
        self.stage_status_banner(action, "started")

        self._stdout = stdout
        self._style = style
        self._prepare_summary = _PrepareSummary()
        
        timestamp = now()
        model_map = {
            "substation": (CleanSubstationDataRequirement, SubstationCleanedDataStorage),
            "connection_application": (CleanConnectionApplicationDataRequirement, ConnectionApplicationCleanedDataStorage)
        }
        pydantic_model, django_model = model_map[self.data_category]
        prev_cleaned_data_storage_objs = list(django_model.objects.filter(reference=self.reference))

        raw_payload_json = self._query_data()
        cleaned_df = self._clean_data(raw_payload_json)
        print(cleaned_df)
        valid_cleaned_data_rows = self._validate_cleaned_data(cleaned_df, pydantic_model)
        self._store_validated_data(valid_cleaned_data_rows, django_model, timestamp)
        self._delete_previous_cleaned_data(prev_cleaned_data_storage_objs)

        if self._prepare_summary.total_stored_valid_data_rows == self._prepare_summary.total_valid_data_rows:
            self.mark_section("-")
            self.stage_status_message(action, "completed successfully", style_category="success")

        self.stage_status_banner(action, "finished")

    def _query_data(self):
        self.log(f"Querying data from {RawFetchedDataStorage._meta.db_table} ...")
        fetched_data_obj = RawFetchedDataStorage.objects.get(reference=self.reference)
        raw_payload_json = fetched_data_obj.raw_payload_json
        return raw_payload_json

    def _clean_data(self, raw_payload_json):
        self.log(f"Commencing data clean...")
        df = self.clean_func(raw_payload_json, self.log)
        self.log(f"Data cleaning completed successfully.", style_category="success")
        return df

    def _validate_cleaned_data(self, df, pydantic_model):
        self.log(f"Commencing data validation...")
        cleaned_data_rows = list(df.iterrows())
        self._prepare_summary.total_cleaned_data_rows = len(cleaned_data_rows)
        total = self._prepare_summary.total_cleaned_data_rows
        update_freq_amount = self._prepare_summary.update_freq_amount(total)

        for i, row in cleaned_data_rows:
            j = i + 1
            record = row.to_dict()
            try:
                validated = pydantic_model(**record)
                self._prepare_summary.valid_cleaned_data_rows.append(validated)
            except Exception as e:
                ext_id = record.get("external_identifier") or record.get("_id")
                self._prepare_summary.invalid_cleaned_data_rows.append(ext_id)
                self.log(f"Skipped invalid row (external_identifier={ext_id}): {e}", style_category="warning",)

            if j % update_freq_amount == 0 or j == total:
                self.log(f"Attempted validation of {j}/{total} rows... (successful: {len(self._prepare_summary.valid_cleaned_data_rows)}, failed: {len(self._prepare_summary.invalid_cleaned_data_rows)})")

        invalid_cleaned_data_rows = self._prepare_summary.invalid_cleaned_data_rows
        total_invalid_cleaned_data_rows = len(invalid_cleaned_data_rows)
        total_valid_cleaned_data_rows = total - total_invalid_cleaned_data_rows
        self._prepare_summary.total_valid_data_rows = total_valid_cleaned_data_rows

        if total_invalid_cleaned_data_rows != 0:
            self.log(
                f"{total_valid_cleaned_data_rows} / {total} cleaned rows validated successfully.", 
                style_category="warning",
            )
            self.log(
                f"The following rows failed to validate (external_identifiers): {', '.join(invalid_cleaned_data_rows)}",
                style_category="warning",
            )
        else:
            self.log("All cleaned data validated.", style_category="success")
        
        return self._prepare_summary.valid_cleaned_data_rows


    def _store_validated_data(self, validated_data, django_model, timestamp):
        self.log("Storing validated cleaned data...")
        total = self._prepare_summary.total_valid_data_rows 
        

        if total == 0:
            self.log("No validated data to store.", style_category="warning")
            return 

        update_freq_amount = self._prepare_summary.update_freq_amount(total)

        for idx, validated in enumerate(validated_data, start=1):
            ext_id = getattr(validated, "external_identifier", None)
            try:
                django_model.objects.create(
                    **validated.model_dump(),
                    prepared_at=timestamp,
                    )
                self._prepare_summary.successful_storage_valid_cleaned_data_rows.append(ext_id)
            except Exception as e:
                self._prepare_summary.failed_storage_valid_cleaned_data_rows.append(ext_id)
                self.log(
                    f"Failed to store row (external_identifier={ext_id}): {e}",
                    style_category="error",
                )

            if idx % update_freq_amount == 0 or idx == total:
                self.log(f"Attempted {idx}/{total} rows... (successful: {len(self._prepare_summary.successful_storage_valid_cleaned_data_rows)}, failed: {len(self._prepare_summary.failed_storage_valid_cleaned_data_rows)})")

        failed_storage_valid_cleaned_data_rows = self._prepare_summary.failed_storage_valid_cleaned_data_rows
        total_invalid_cleaned_data_rows = len(failed_storage_valid_cleaned_data_rows)
        total_stored_valid_data_rows = total - total_invalid_cleaned_data_rows
        self._prepare_summary.total_stored_valid_data_rows = total_stored_valid_data_rows       

        if self._prepare_summary.failed_storage_valid_cleaned_data_rows != []:
            self.log(
                f"{total_stored_valid_data_rows}/{total} cleaned rows stored successfully.", style_category="warning",)
            self.log(
                f"The following rows failed to store (external_identifiers): {', '.join(failed_storage_valid_cleaned_data_rows)}",
                style_category="error",
            )
        else:
            self.log(f"All storage of {total} cleaned rows stored successfully.", style_category="success",)

    def _delete_previous_cleaned_data(self, prev_cleaned_data_storage_objs):
        if prev_cleaned_data_storage_objs:
            self.log(f"Deleting previously stored data...")
            for obj in prev_cleaned_data_storage_objs:
                obj.delete()

        



