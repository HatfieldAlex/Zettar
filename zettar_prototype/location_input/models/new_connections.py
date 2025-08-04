from django.db import models
from django.contrib.gis.db import models as gis_models
from .substations import PrimarySubstation, BSPSubstation, GSPSubstation, DNOGroup 
from .shared_fields import ConnectionVoltageLevel
from location_input.constants import VOLTAGE_CHOICES


class ConnectionStatus(models.Model):
    STATUS_CHOICES = [
        ('budget', 'Budget Estimate Provided'),
        ('pending', 'Connection Offer – Pending Acceptance'),
        ('accepted', 'Connection Offer – Accepted'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
    )

    
class ReportingPeriod(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        unique_together = ('start_date', 'end_date')


class NewConnection(models.Model):

    connection_status = models.ForeignKey(
        ConnectionStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='new_connections'
    )

    connection_voltage_level = models.ForeignKey(
        ConnectionVoltageLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='new_connections'
    )

    reporting_period = models.ForeignKey(
        ReportingPeriod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='new_connections'
    )

    primary_substation = models.ForeignKey(
        PrimarySubstation,
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='new_connections'
    )

    bsp_substation = models.ForeignKey(
        BSPSubstation,
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='new_connections'
    )

    gsp_substation = models.ForeignKey(
        GSPSubstation,
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='new_connections'
    )

    dno_group = models.ForeignKey(
        DNOGroup, 
        on_delete=models.CASCADE, 
        related_name='new_connections',
        null=True, 
        blank=True,
    )

    demand_count = models.PositiveIntegerField(blank=True, null=True)

    total_demand_capacity_mw =  models.DecimalField(
        max_digits=10, decimal_places=3,
        help_text="Total demand capacity in megawatts (MW)"
        )

    generation_count = models.PositiveIntegerField(blank=True, null=True)
    total_generation_capacity_mw =  models.DecimalField(
        max_digits=10, decimal_places=3,
         help_text="Total generation capacity in megawatts (MW)"
        )

    def clean(self):
        substation_fields = [
            self.primary_substation,
            self.bsp_substation,
            self.gsp_substation,
        ]
        filled_substation_fields = sum(s is not None for s in substation_fields)
        if filled_substation_fields != 1:
            raise ValidationError("Exactly one of primary, BSP, or GSP substation must be set.")
