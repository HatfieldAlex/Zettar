from django.db import models
from django.contrib.gis.db import models as gis_models
from django_pydantic_field import SchemaField
from django.utils import timezone

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
    reference = models.CharField(max_length=255)

class SubstationCleanedDataStorage(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=SUBSTATION_TYPE_CHOICES)
    candidate_voltage_levels_kv = models.JSONField(default=list)
    external_identifier = models.CharField(max_length=255, null=True, blank=True)
    geolocation = gis_models.PointField(geography=True)
    dno_group = models.CharField(max_length=255, choices=DNO_GROUP_CHOICES)
    prepared_at = models.DateTimeField()
    reference = models.CharField(max_length=255)


CONNECTION_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('budget', 'Budget'),
    ('accepted', 'Accepted'),
]


class ConnectionApplicationCleanedDataStorage(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=SUBSTATION_TYPE_CHOICES)
    dno_group = models.CharField(max_length=255, choices=DNO_GROUP_CHOICES)
    candidate_voltage_levels_kv = models.JSONField(default=list)
    geolocation = gis_models.PointField(geography=True, null=True, blank=True)

    proposed_voltage = models.DecimalField(max_digits=4, decimal_places=1)
    connection_status = models.CharField(
        max_length=20,
        choices=CONNECTION_STATUS_CHOICES,
        default='pending',
    )
    total_demand_number = models.IntegerField()
    total_demand_capacity_mw = models.DecimalField(max_digits=10, decimal_places=3)
    total_generation_number = models.IntegerField()
    total_generation_capacity_mw = models.DecimalField(max_digits=10, decimal_places=3)
    
    external_identifier = models.CharField(max_length=255, null=True, blank=True)
    prepared_at = models.DateTimeField(default=timezone.now)
    reference = models.CharField(max_length=255)

