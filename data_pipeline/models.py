from django.db import models
from django.contrib.gis.db import models as gis_models
from django_pydantic_field import SchemaField

CONTENT_TYPE_CHOICES = [
    ("substation", "Substations"),
    ("connection_application", "Connection Applications"),
]

SUBSTATION_TYPE_CHOICES = [
    ("primary", "Primary Substation"),
    ("bsp", "Bulk Supply Point"),
    ("gsp", "Grid Supply Point"),
]

DNO_GROUP_CHOICES = [
    ("nged", "NGED"),
]

class RawFetchedDataStorage(models.Model):
    data_category = models.CharField(max_length=255, choices=CONTENT_TYPE_CHOICES)
    dno_group = models.CharField(max_length=255, choices=DNO_GROUP_CHOICES)
    raw_payload_json = models.JSONField()
    source_url = models.URLField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)


class SubstationCleanedDataStorage(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=SUBSTATION_TYPE_CHOICES)
    candidate_voltage_levels_kv = models.JSONField(default=list)
    external_identifier = models.CharField(max_length=255, null=True, blank=True)
    geolocation = gis_models.PointField(geography=True)
    dno_group = models.CharField(max_length=255, choices=DNO_GROUP_CHOICES)
    reference = models.IntegerField(db_index=True, null=True, blank=True)

    raw_data_record = models.ForeignKey(
        "RawFetchedDataStorage",   
        on_delete=models.SET_NULL, 
        null=True,          
        blank=True,          
        related_name="cleaned_substations", 
    )

class ConnectionApplicationCleanedDataStorage(models.Model):
    pass
