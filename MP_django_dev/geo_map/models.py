# Import for postgres ArrayField
from django.contrib.postgres.fields import ArrayField

# Import for the postgis elements in the db
from django.contrib.gis.db import models

# Create your models here.


class GeoLocation(models.Model):

    # Field which denotes the geo_id
    # geo_id = models.IntegerField(null=False, blank=False)

    # Lat and long coordinates
    latitude = models.FloatField(null=False, blank=False)
    longitude = models.FloatField(null=False, blank=False)
    # Geometry of lat long coorginates
    # location = models.PointField(null=True, blank=True)


class GeoTweet(models.Model):

    # Field which denotes the tweet_id
    # tweet_id = models.IntegerField(null=False, blank=False)
    # field which points to the location of the tweet
    geo_location = models.ForeignKey(GeoLocation, models.CASCADE, null=False)
