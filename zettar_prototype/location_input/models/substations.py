from django.db import models
from django.contrib.gis.db import models as gis_models

class DNOGroup(models.Model):
    DNO_GROUP_CHOICES = [
        ('UKPN', 'UK Power Networks'),
        ('NGED', 'National Grid Electricity Distribution'),
        ('SPEN', 'SP Energy Networks'),
        ('NP', 'Northern Powergrid'),
        ('ENW', 'Electricity North West'),
        ('SSEN', 'Scottish and Southern Electricity Networks'),
    ]
    abbreviation = models.CharField(
        max_length=10,
        choices=DNO_GROUP_CHOICES,
        unique=True,
    )

class DNOLicenceArea(models.Model):

    dno_group = models.ForeignKey(DNOGroup, on_delete=models.CASCADE, related_name='licence_areas')

    DNO_LICENCE_CHOICES = [
        ('north_west_england', 'North West England'),
        ('north_east_england', 'North East England'),
        ('yorkshire', 'Yorkshire'),
        ('north_scotland', 'North Scotland'),
        ('southern_england', 'Southern England'),
        ('merseyside_cheshire_north_wales', 'Merseyside, Cheshire, North Wales'),
        ('central_southern_scotland', 'Central & Southern Scotland'),
        ('london', 'London'),
        ('eastern_england', 'Eastern England'),
        ('south_east_england', 'South East England'),
        ('east_midlands', 'East Midlands'),
        ('west_midlands', 'West Midlands'),
        ('south_west_england', 'South West England'),
        ('south_wales', 'South Wales'),
    ]

    licence_area = models.CharField(max_length=50, choices=DNO_LICENCE_CHOICES)

class DataPublicationDate(models.Model):
    date = models.DateField(auto_now_add=True)

class GSPSubstation(models.Model):
    name = models.CharField(max_length=255)
    geolocation = gis_models.PointField(blank=True, null=True)

    licence_area = models.ForeignKey(
        DNOLicenceArea,
        on_delete=models.CASCADE,
        related_name='gsp_substations'
    )

class BSPSubstation(models.Model):
    name = models.CharField(max_length=255)
    geolocation = gis_models.PointField(blank=True, null=True)

    gsp_substation = models.ForeignKey(
        GSPSubstation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='bsp_substations'
    )

class PrimarySubstation(models.Model):
    name = models.CharField(max_length=255)
    geolocation = gis_models.PointField(blank=True, null=True)

    bsp_substation = models.ForeignKey(
        BSPSubstation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='primary_substations'
    )
