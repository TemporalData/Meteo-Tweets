# Import for postgres ArrayField
from django.contrib.postgres.fields import ArrayField

# Import for the postgis elements in the db
from django.contrib.gis.db import models

# Create your models here.


class GeoLocation(models.Model):
    # Lat and long coordinates
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    # Geometry of lat long coorginates
    location = models.PointField(null=True, blank=True)


class GeoData(models.Model):
    geo_location = models.ForeignKey(GeoLocation, models.CASCADE, null=False)


class GeoCache(models.Model):
    field_name = models.TextField(null=False)
    data_list = ArrayField(models.FloatField())
