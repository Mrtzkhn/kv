from django.db import models


class KeyValue(models.Model):
    key = models.CharField(max_length=255, unique=True)  # unique implies an index
    value = models.TextField(blank=True, default="")

    def __str__(self):
        return self.key
