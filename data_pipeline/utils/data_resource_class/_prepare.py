from dataclasses import dataclass, field
import pandas as pd
from django.contrib.gis.geos import Point as GEOSPoint
from data_pipeline.models import RawFetchedDataStorage, SubstationCleanedDataStorage, ConnectionApplicationCleanedDataStorage
from .validators import CleanSubstationDataRequirement, CleanConnectionApplicationDataRequirement
from django.utils.timezone import now
from typing import Dict, Union, Callable, Any

@dataclass
class _CleaningHelpers:
    extract_payload_func: Callable[[dict], Any]  = lambda parsed_resp: parsed_resp["result"]["records"]
    drop_headers: Dict[str, set] = field(default_factory=dict)
    exclusions: Dict[str, set] = field(default_factory=dict)

    construct_external_identifier: Callable[[pd.Series], str] = field(
        default_factory=lambda: (lambda row: str(row.get("external_identifier", "")))
    )
    construct_geolocation: Callable[[pd.Series], GEOSPoint] = field(
        default_factory=lambda: (lambda row: GEOSPoint(0, 0, srid=4326))
    )
    construct_name: Callable[[pd.Series], str] = field(
        default_factory=lambda: (lambda row: str(row.get("name", "")))
    )
    construct_type: Callable[[pd.Series], str] = field(
        default_factory=lambda: (lambda row: str(row.get("type", "")))
    ) 

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
        cleaning_helpers = self.cleaning_helpers
        raw_parsed_response = self._query_data()
        raw_payload_json = self._extract_payload(cleaning_helpers, raw_parsed_response)
        cleaned_df = self._clean_data(raw_payload_json, cleaning_helpers)
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

    def _extract_payload(self, cleaning_helpers, raw_parsed_response):
        self.log("Extracting payload ...")
        payload = cleaning_helpers.extract_payload_func(raw_parsed_response)
        return payload



    def _clean_data(
    self, 
    raw_payload_json: Union[dict[str, Any], list[dict[str, Any]]],
    cleaning_helpers: _CleaningHelpers,
    ) -> pd.DataFrame:

        self.log("Converting raw JSON payload into DataFrame...")
        df = pd.DataFrame.from_records(raw_payload_json)

        self.log("Dropping columns not required...")
        df.drop(columns=cleaning_helpers.drop_headers["initial"], inplace=True)

        self.log("Dropping rows not required...")
        for col, vals in cleaning_helpers.exclusions.items():
            df = df[~df[col].isin(vals)]
        
        self.log("Creating new columns...")
        for col in {"name", "type", "geolocation", "dno_group", "external_identifier", "reference"}:
            df[col] = None 

        self.log("Transforming rows...")
        for row in df.itertuples(index=True):
            try:
                row_dict = row._asdict()
                df.at[row.Index, "name"] = cleaning_helpers.construct_name(row_dict)
                df.at[row.Index, "type"] = cleaning_helpers.construct_type(row_dict)
                df.at[row.Index, "geolocation"] = cleaning_helpers.construct_geolocation(row_dict)
                df.at[row.Index, "dno_group"] = self.dno_group
                df.at[row.Index, "external_identifier"] = cleaning_helpers.construct_external_identifier(row_dict)
                df.at[row.Index, "reference"] = self.reference
            except Exception as e:
                self.log(
                    f"Error transforming row: {row_dict} -- {e}",
                    style_category="error"
                )
                raise
        # df["name"] = df.apply(cleaning_helpers.construct_name, axis=1)
        # df["type"] = df.apply(cleaning_helpers.construct_type, axis=1)
        # df["geolocation"] = df.apply(cleaning_helpers.construct_geolocation, axis=1)
        # df["dno_group"] = self.dno_group
        # df["external_identifier"] = df.apply(cleaning_helpers.construct_external_identifier, axis=1)
        # df["reference"] = self.reference

    
            

        self.log("Dropping columns only required for transformation...")
        df.drop(columns=cleaning_helpers.drop_headers["subsequent"], inplace=True)
        
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

        



