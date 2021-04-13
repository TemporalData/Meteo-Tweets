from django.db import models
from datetime import timezone

# Create your models here.


class TimeData(models.Model):
    # tweet_id = models.IntegerField(null=False)
    time_created = models.DateTimeField(null=False)
    date = models.TextField(max_length=11)
