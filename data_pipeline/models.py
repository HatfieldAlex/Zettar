from django.db import models

CONTENT_TYPE_CHOICES = [
    ("substations", "Substations"),
    ("connection_applications", "Connection Applications"),
]

DNO_GROUP_CHOICES = [
    ("nged", "NGED"),
]


class RawDataRecord(models.Model):

    data_category = models.CharField(
        max_length=50,
        choices=CONTENT_TYPE_CHOICES,
    )

    dno_group = models.CharField(
        max_length=10,
        choices=DNO_GROUP_CHOICES,
    )

    raw_data = models.TextField(
        help_text="Raw response data (usually JSON, but can handle other formats like XML, HTML, etc.)"
    )

    source_url = models.URLField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.content_type} ({self.dno_group}) @ {self.fetched_at.strftime('%Y-%m-%d %H:%M:%S')}"
