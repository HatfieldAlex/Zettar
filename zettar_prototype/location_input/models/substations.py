from django.db import models
from django.contrib.gis.db import models as gis_models

class DNOGroup(models.Model):
    abbr = models.CharField(
        max_length=10,
        unique=True,
        null=True, 
        blank=True,
    )

class GSPSubstation(models.Model):
    name = models.CharField(max_length=255)
    geolocation = gis_models.PointField(blank=True, null=True)

    dno_group = models.ForeignKey(
        DNOGroup, 
        on_delete=models.CASCADE, 
        related_name='gsp_substations',
        null=True, 
        blank=True,
    )

class BSPSubstation(models.Model):
    name = models.CharField(max_length=255)
    geolocation = gis_models.PointField(blank=True, null=True)

    dno_group = models.ForeignKey(
        DNOGroup, 
        on_delete=models.CASCADE, 
        related_name='bsp_substations',
        null=True, 
        blank=True,
    )

class PrimarySubstation(models.Model):
    name = models.CharField(max_length=255)
    geolocation = gis_models.PointField(blank=True, null=True)

    dno_group = models.ForeignKey(
        DNOGroup, 
        on_delete=models.CASCADE, 
        related_name='primary_substations',
        null=True, 
        blank=True,
    )