from django.db import models

# Import for postgres ArrayField
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class GeoData(models.Model):
    tweet_id = models.IntegerField(null=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)


class GeoCache(models.Model):
    field_name = models.TextField(null=False)
    data_list = ArrayField(models.FloatField())