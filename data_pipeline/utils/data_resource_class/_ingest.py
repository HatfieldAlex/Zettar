import requests
from data_pipeline.models import RawFetchedDataStorage
from dataclasses import dataclass

class _DataResourceIngest:



    def ingest(self, stdout=None, style=None) -> bool:
        success_bool = False
        action = "ingest"
        self._stdout = stdout
        self._style = style

        self.stage_status_banner(action, "started")
        self.log(f"Fetching data from {self.url} ...")

        try:
            response = requests.get(
                self.url, 
                params=self.query_params or None, 
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            self.log(f"Data successfully fetched", style_category="success")

            self.log(f"Extracting payload ...")
            self.extract_payload_func(response)
            self.log(f"Payload successfully extracted")

            self.log(f"Storing fetched data in {RawFetchedDataStorage._meta.db_table} ...")
            raw_data_storage = RawFetchedDataStorage.objects.create(
                data_category=self.data_category,
                dno_group=self.dno_group,
                source_url=self.url,
                raw_response_json=self.extract_payload_func(response)
                )

            if raw_data_storage.id:
                self.log(f"Data successfully stored (id: {raw_data_storage.id})", style_category="success")

                if self.raw_data_storage_id:
                    self.log(f"Deleting previously fetched data (id: {self.raw_data_storage_id}) ...")
                    RawFetchedDataStorage.objects.filter(id=self.raw_data_storage_id).delete()
                    self.log("Previously fetched data deleted")
                    
                self.raw_data_storage_id = raw_data_storage.id
                self.mark_section("-")
                self.stage_status_message(action, "completed successfully", style_category="success")
                success_bool = True    

            else:
                self.log(f"Failed to store data", style_category="error")
        except requests.RequestException as e: 
            self.log(f"Failed to fetch data: {e}", style_category="error")
        
        finally:
            self.stage_status_banner(action, "finished")
            return success_bool

