from django.db import models
from django.contrib.gis.db import models as gis_models


class DNOGroup(models.Model):
    abbr = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.abbr or "Unnamed DNOGroup"


class SubstationType(models.Model):
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.code


class Substation(models.Model):
    name = models.CharField(max_length=255)
    geolocation = gis_models.PointField(blank=True, null=True)

    dno_group = models.ForeignKey(
        DNOGroup,
        on_delete=models.CASCADE,
        related_name="substations",
        null=True,
        blank=True,
    )

    type = models.ForeignKey(
        SubstationType,
        on_delete=models.PROTECT,
        related_name="substations"
    )

    external_identifier = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["dno_group", "external_identifier"],
                name="unique_dno_group_external_identifier"
            )
        ]

    def __str__(self):
        return self.name


__all__ = [
    "DNOGroup",
    "Substation",
    "SubstationType",
]
