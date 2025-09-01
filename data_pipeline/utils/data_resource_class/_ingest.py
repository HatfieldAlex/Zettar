import requests
from data_pipeline.models import RawFetchedDataStorage
from dataclasses import dataclass
from django.core.exceptions import ValidationError
from django.db import transaction


class _DataResourceIngest:
    def ingest(self, stdout=None, style=None) -> bool:
        self._stdout = stdout
        self._style = style
        action = "ingest"
        self.stage_status_banner(action, "started")
        prev_fetched_data_storage_obj = RawFetchedDataStorage.objects.filter(reference=self.reference).order_by("fetched_at").first()

        try:
            response = self._fetch_data()
            parsed_response_json = self._parse_response(response)
            with transaction.atomic():
                self._store_payload(parsed_response_json)
                self._delete_prior_payload(prev_fetched_data_storage_obj)
        
            self.mark_section("-")
            self.stage_status_message(action, "completed successfully", style_category="success")
            return True   
                
        except ValidationError as e:
            self.log(f"Validation error: {e}", style_category="error")

        except requests.RequestException as e: 
            self.log(f"Failed to fetch data: {e}", style_category="error")

        except Exception as e:
            self.log(f"Unexpected error during ingest: {e}", style_category="error")
        
        finally:
            self.stage_status_banner(action, "finished")

    def _parse_response(self, response):
        self.log("Transforming response into a structured format...")
        return self.parse_raw_response_func(response)

    def _fetch_data(self):
        self.log(f"Fetching data from {self.url} ...")
        response = requests.get(
            self.url, 
            params=self.query_params or None, 
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        self.log(f"Data successfully fetched", style_category="success")
        return response

    def _store_payload(self, raw_payload_json):
        self.log(f"Storing fetched data in {RawFetchedDataStorage._meta.db_table} ...")
        raw_data_storage = RawFetchedDataStorage(
            reference=self.reference,
            data_category=self.data_category,
            dno_group=self.dno_group,
            source_url=self.url,
            raw_payload_json=raw_payload_json
            )
        
        raw_data_storage.full_clean()
        raw_data_storage.save()

        self.log(f"Data successfully stored (id: {raw_data_storage.id})", style_category="success")
        return 


    def _delete_prior_payload(self, prev_fetched_data_storage_obj):
        if not prev_fetched_data_storage_obj:
            return

        self.log(f"Deleting previously fetched data (id: {prev_fetched_data_storage_obj.id}) ...")
        prev_fetched_data_storage_obj.delete()
        self.log("Previously fetched data deleted")

