from django.db import models

# Create your models here.
import pandas as pd


class RegionTopic(models.Model):
	# cluster_idx = models.ForeignKey(Document, related_name=cluster_idx, on_delete=models.CASCADE)
	cluster_idx = models.IntegerField(default=-1)
	topic_idx = models.IntegerField(null=True,default=None)
	topic_prob = models.FloatField(null=True,default=None,blank=True)
	# keywords = models.TextField(default=None,blank=True) #list of (keyword, prob) by ldamodel.show_topic(11)
	
	def __str__(self):
		return str(self.cluster_idx)
	class Meta:
		ordering = ['cluster_idx']


class TopicWord(models.Model):
	c_t_idx = models.ForeignKey(RegionTopic,on_delete=models.CASCADE)
	keyword = models.CharField(blank=True,max_length=50)
	keyword_prob = models.FloatField(null=True,default=None,blank=True)





# Define the relational table for original 'partial.csv'
class Document(models.Model):
	doc_idx = models.IntegerField(blank=True)
	user_name = models.CharField(blank=True, max_length=50)
	latitude = models.FloatField(null=True, blank=True)
	longitude = models.FloatField(null=True, blank=True)
	pub_date = models.DateField(auto_now=False, auto_now_add=False)
	text = models.TextField(blank=True)
	cluster_idx = models.ForeignKey(RegionTopic, on_delete=models.CASCADE) #-1: noise
	# cluster_id = models.ForeignKey(Cluster, on_delete=models.SET_NULL)
	
	# weather_event = models.JSONField()

	def __str__(self):
		return str(self.doc_idx) #, self.cluster_idx

	class Meta:
		ordering = ['doc_idx'] #'cluster_idx'

# class Cluster(models.Model):
# 	cluster_id = models.IntegerField(default=-1) #-1: noise
# 	c_lati = models. FloatField()
# 	c_long = models.FloatField()
# 	num_doc = models.IntegerField(default=0) # count of documents per cluster
# 	def __str__(self):
# 		return self.cluster_id
# 	class Meta:
# 		ordering = ['cluster_id']


# Not related to a particular cluster, save in 'weather_terms.csv'
class DocWeatherEvent(models.Model):
	event = models.CharField(max_length=30,blank=True)
	doc_idx = models.ManyToManyField(Document, blank=True)
	
	# def __str__(self):
	# 	return self.event


