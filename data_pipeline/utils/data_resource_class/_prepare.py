from dataclasses import dataclass, field
import pandas as pd
from data_pipeline.models import RawFetchedDataStorage, SubstationCleanedDataStorage, ConnectionApplicationCleanedDataStorage
from .validators import CleanSubstationDataRequirement, CleanConnectionApplicationDataRequirement
from django.utils.timezone import now
from typing import Dict, Union, Callable, Any


@dataclass
class _CleaningHelpers:
    drop_headers: Dict[str, set] = field(default_factory=dict)
    exclusions: Dict[str, set] = field(default_factory=dict)
    additional_columns: set[str] = field(default_factory=set) 
    transform_row: Callable[[pd.Series], pd.Series] = field(default_factory=lambda: (lambda row: row))

    name_alias: str = "Substation Name"
    type_alias: str = "Substation Type"
    external_identifier: str = "_id"

    primary_alias: str = "Primary Substation"
    bsp_alias: str = "Bulk Supply Point"
    gsp_alias: str = "Grid Supply Point"


    @property
    def raw_to_standard_headers(self) -> Dict[str, str]:
        return {
            self.name_alias: "name",
            self.type_alias: "type",
            self.external_identifier: "external_identifier",
        }

    @property
    def raw_to_standard_type_values(self) -> Dict[str, str]:
        return {
            self.primary_alias: "primary",
            self.bsp_alias: "bsp",
            self.gsp_alias: "gsp",
        }

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

@dataclass
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
        cleaned_df = self._clean_data(raw_payload_json, self.cleaning_helpers)
        valid_cleaned_data_rows = self._validate_cleaned_data(cleaned_df, pydantic_model)
        self._store_validated_data(valid_cleaned_data_rows, django_model, timestamp)
        self._delete_previous_cleaned_data(prev_cleaned_data_storage_objs)

        if self._prepare_summary.total_stored_valid_data_rows == self._prepare_summary.total_valid_data_rows:
            self.mark_section("-")
            self.stage_status_message(action, "completed successfully", style_category="success")

        self.stage_status_banner(action, "finished")

    def _clean_data(
    self, 
    raw_payload_json: Union[dict[str, Any], list[dict[str, Any]]],
    cleaning_helpers: _CleaningHelpers,
    ) -> pd.DataFrame:

        self.log("Converting raw JSON payload into DataFrame...")
        df = pd.DataFrame.from_records(raw_payload_json)

        self.log("Dropping columns not required...")
        df.drop(columns=cleaning_helpers.drop_headers["initial"], inplace=True)
        
        self.log("Creating new columns...")
        for header in cleaning_helpers.additional_columns:
            if header not in df.columns:
                df[header] = None
        
        self.log("Standardising header names...")
        df = df.rename(columns=cleaning_helpers.raw_to_standard_headers)

        self.log("Dropping rows not required...")
        for col, vals in cleaning_helpers.exclusions.items():
            df = df[~df[col].isin(vals)]

        self.log("Standardising substation values...")
        df["type"] = df["type"].replace(cleaning_helpers.raw_to_standard_type_values)

        self.log("Transforming rows...")
        df = df.apply(cleaning_helpers.transform_row, axis=1)        

        self.log("Dropping columns only required for transformation...")
        df.drop(columns=cleaning_helpers.drop_headers["subsequent"], inplace=True)
        
        return df


    def _query_data(self):
        self.log(f"Querying data from {RawFetchedDataStorage._meta.db_table} ...")
        fetched_data_obj = RawFetchedDataStorage.objects.get(reference=self.reference)
        raw_payload_json = fetched_data_obj.raw_payload_json
        return raw_payload_json

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

        



