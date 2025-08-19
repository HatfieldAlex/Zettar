import requests
from data_pipeline.models import RawFetchedDataStorage
from dataclasses import dataclass
from django.core.exceptions import ValidationError

class _DataResourceIngest:
    def ingest(self, stdout=None, style=None) -> bool:
        self._stdout = stdout
        self._style = style
        action = "ingest"
        self.stage_status_banner(action, "started")
        
        try:
            response = self._fetch_data()
            raw_payload_json = self._extract_payload(response)
            raw_data_storage_id = self._store_payload(raw_payload_json)
            self._delete_prior_payload(raw_data_storage_id)

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

    def _extract_payload(self, response):
        self.log("Extracting payload ...")
        payload = self.extract_payload_func(response)
        self.log("Payload successfully extracted")
        return payload

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
            data_category=self.data_category,
            dno_group=self.dno_group,
            source_url=self.url,
            raw_payload_json=raw_payload_json
            )

        raw_data_storage.full_clean()
        raw_data_storage.save()
        raw_data_storage_id = raw_data_storage.id
        self.log(f"Data successfully stored (id: {raw_data_storage_id})", style_category="success")
        return raw_data_storage_id


    def _delete_prior_payload(self, current_raw_data_storage_id):
        raw_data_storage_id = self.raw_data_storage_ref

        if raw_data_storage_id:
            self.log(f"Deleting previously fetched data (id: {raw_data_storage_id}) ...")
            RawFetchedDataStorage.objects.filter(id=raw_data_storage_id).delete()
            self.log("Previously fetched data deleted")
            self.raw_data_storage_ref = current_raw_data_storage_id

        self.raw_data_storage_ref = current_raw_data_storage_id
