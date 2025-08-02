from decimal import Decimal
from django.db import models
from location_input.utils.constants import VOLTAGE_CHOICES

class ConnectionVoltageLevel(models.Model):
    level_kv = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        choices=VOLTAGE_CHOICES,
    )
