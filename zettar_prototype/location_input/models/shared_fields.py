from django.db import models

class ConnectionVoltageLevel(models.Model):
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
