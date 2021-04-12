from django.db import models

# Create your models here.


class TimeData(models.Model):
    tweet_id = models.IntegerField(null=False)
    time_created = models.DateTimeField(null=False)
    date = models.TextField(max_length=11)
