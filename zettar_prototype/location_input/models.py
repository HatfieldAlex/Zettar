from django.db import models
from django.contrib.gis.db import models as gis_models


class Substations(models.Model):
    id = models.AutoField(primary_key=True)
    substation_nged_id = models.IntegerField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)
    area = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    substationnumber = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    primary = models.TextField(blank=True, null=True)
    bsp = models.TextField(blank=True, null=True)
    gsp = models.TextField(blank=True, null=True)
    demandconnectedheadroommw = models.FloatField(blank=True, null=True)
    demandcontractedheadroommw = models.FloatField(blank=True, null=True)
    demandconnectedrag = models.TextField(blank=True, null=True)
    demandcontractedrag = models.TextField(blank=True, null=True)
    generationtotalcapacity = models.FloatField(blank=True, null=True)
    generationconnectedheadroommw = models.FloatField(blank=True, null=True)
    generationcontractedheadroommw = models.FloatField(blank=True, null=True)
    generationquotedcapacity = models.FloatField(blank=True, null=True)
    generationconnectedrag = models.TextField(blank=True, null=True)
    generationcontractedrag = models.TextField(blank=True, null=True)
    geolocation = gis_models.PointField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'substations'
