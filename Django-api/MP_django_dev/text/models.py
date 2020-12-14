from django.db import models

# Create your models here.


class RegionTopic(models.Model):
    cluster_idx = models.IntegerField(default=-1)
    topic_idx = models.IntegerField(null=True, default=None)
    topic_prob = models.FloatField(null=True, default=None, blank=True)

    def __str__(self):
        return str(self.cluster_idx)

    class Meta:
        ordering = ['cluster_idx']


class TopicWord(models.Model):
    c_t_idx = models.ForeignKey(RegionTopic, on_delete=models.CASCADE)
    keyword = models.CharField(blank=True, max_length=50)
    keyword_prob = models.FloatField(null=True, default=None, blank=True)


# Define the relational table for original 'partial.csv'
class Document(models.Model):
    doc_idx = models.IntegerField(blank=True)
    user_name = models.CharField(blank=True, max_length=50)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    pub_date = models.DateField(auto_now=False, auto_now_add=False)
    text = models.TextField(blank=True)
    cluster_idx = models.ForeignKey(RegionTopic, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.doc_idx)  # , self.cluster_idx

    class Meta:
        ordering = ['doc_idx']  # 'cluster_idx'


# Not related to a particular cluster, save in 'weather_terms.csv'
class DocWeatherEvent(models.Model):
    event = models.CharField(max_length=30, blank=True)
    doc_idx = models.ManyToManyField(Document, blank=True)
