# Import for postgres ArrayField
from django.contrib.postgres.fields import ArrayField

# Import for the postgis elements in the db
from django.contrib.gis.db import models

# Create your models here.


class GeoData(models.Model):
    tweet_id = models.IntegerField(null=False)
    location = models.PointField(null=True, default=None)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)


class GeoCache(models.Model):
    field_name = models.TextField(null=False)
    data_list = ArrayField(models.FloatField())
