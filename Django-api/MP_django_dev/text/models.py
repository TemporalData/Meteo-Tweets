from django.db import models

# Create your models here.
import pandas as pd


class TermType(models.Model):
    typename = models.CharField(max_length=30)

    def __str__(self):
        return self.typename


class WeatherTerm(models.Model):
    term = models.CharField(max_length=30, blank=True)
    ttype = models.ForeignKey(TermType, on_delete=models.RESTRICT, null=True, blank=True)

    def __str__(self):
        return self.term

# Define the relational table for original 'partial_clean_term.csv'; (or 'test.csv')
# Additional fields can be added, e.g. mention, is_retweet, ...


class Document(models.Model):
    doc_idx = models.IntegerField(blank=True)
    #user_name = models.CharField(blank=True, max_length=50)
    #latitude = models.FloatField(null=True, blank=True)
    #longitude = models.FloatField(null=True, blank=True)
    pub_date = models.DateField(auto_now=False, auto_now_add=False)
    #text = models.TextField(blank=True)
    #raw = models.TextField(blank=True)
    #terms = models.ManyToManyField(WeatherTerm, blank=True)

    def __str__(self):
        return str(self.doc_idx)

    class Meta:
        ordering = ['pub_date', 'doc_idx']
