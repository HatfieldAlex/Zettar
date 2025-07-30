from django.db import models
from django.contrib.gis.db import models as gis_models

class ProposedConnectionVoltageLevel(models.Model):
    VOLTAGE_CHOICES = [
        (6.6, '6.6 kV'),
        (11.0, '11 kV'),
        (33.0, '33 kV'),
        (66.0, '66 kV'),
        (132.0, '132 kV'),
    ]

    level_kv = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        choices=VOLTAGE_CHOICES,
    )


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


class NewConnection(models.Model):

    connection_status = models.ForeignKey(
        ConnectionStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='new_connections'
    )

    voltage_level = models.ForeignKey(
        ProposedConnectionVoltageLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='new_connections'
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
