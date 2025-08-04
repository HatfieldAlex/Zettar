from django.db import models
from location_input.constants import VOLTAGE_CHOICES

class ConnectionVoltageLevel(models.Model):
    level_kv = models.CharField(
        max_length=10,
        choices=VOLTAGE_CHOICES,
    )
