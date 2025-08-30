from django.db import models
from django.contrib.gis.db import models as gis_models

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

    dno_group = models.ForeignKey(
        DNOGroup,
        on_delete=models.CASCADE,
        related_name="substations",
        null=True,
        blank=True,
    )
    type = models.CharField(max_length=10, choices=SUBSTATION_TYPES)
    external_identifier = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["dno_group", "external_identifier"],
                name="unique_dno_group_external_identifier"
            )
        ]

__all__ = [
    "DNOGroup",
    "Substation",
]