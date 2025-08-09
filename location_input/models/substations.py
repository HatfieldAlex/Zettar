from django.db import models
from django.contrib.gis.db import models as gis_models

from .shared_fields import ConnectionVoltageLevel

class DNOGroup(models.Model):
    abbr = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
    )

class Substation(models.Model):
    SUBSTATION_TYPES = [
        ("gsp", "Grid Supply Point"),
        ("bsp", "Bulk Supply Point"),
        ("primary", "Primary"),
    ]

    name = models.CharField(max_length=255)
    geolocation = gis_models.PointField(blank=True, null=True)
    voltage_kv = models.ManyToManyField(
        ConnectionVoltageLevel, related_name="substations", blank=True
    )
    dno_group = models.ForeignKey(
        DNOGroup,
        on_delete=models.CASCADE,
        related_name="substations",
        null=True,
        blank=True,
    )
    type = models.CharField(max_length=10, choices=SUBSTATION_TYPES)

__all__ = [
    "DNOGroup",
    "Substation",
]