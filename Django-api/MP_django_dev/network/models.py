from django.db import models

import pandas as pd

class TweetInfo(models.Model):
    tweet_id = models.IntegerField(primary_key=True)
    date = models.DateField(auto_now=False, auto_now_add=False)
    # place_full_name
    # latitude = models.FloatField(null=True, blank=True)
	# longitude = models.FloatField(null=True, blank=True)
    user_id = models.ForeignKey('UserInfo', on_delete=models.CASCADE)
    is_retweet = models.BooleanField(null=False)
    retweet_count = models.IntegerField(null=False)
    is_reply = models.BooleanField(null=False)
    in_reply_to_status_id = models.IntegerField(null=True, blank=True)
    in_reply_to_user_id = models.IntegerField(null=True, blank=True)
    n_user_mentions = models.IntegerField(null=False)
    ##user_mentions_id = models.IntegerField(null=False)

    def __str__(self):
	    return str(self.tweet_id)

class UserInfo(models.Model):
    user_id = models.IntegerField(primary_key=True)
    user_screen_name = models.CharField(max_length=30, null=True, blank=True)
    user_followers_count = models.IntegerField(null=True, blank=True)
    user_following_count = models.IntegerField(null=True, blank=True)
    user_favourited_other_tweets_count = models.IntegerField(null=True, blank=True)

    def __str__(self):
	    return str(self.user_id)

""" class UserReply(models.Model):
    id = models.AutoField(primary_key=True)
    tweet_id = models.ForeignKey('TweetInfo', on_delete=models.CASCADE)
    user_id = models.ForeignKey('UserInfo', on_delete=models.CASCADE)
    in_reply_to_user_id = models.ForeignKey('UserInfo', on_delete=models.CASCADE)

class UserMention(models.Model): 
    id = models.AutoField(primary_key=True)
    tweet_id = models.ForeignKey('TweetInfo', on_delete=models.CASCADE)
    user_id = user_id = models.ForeignKey('UserInfo', on_delete=models.CASCADE)
    uder_mention_id = models.ForeignKey('UserInfo', on_delete=models.CASCADE)

class Graph_Edge(models.Model):
    id = models.AutoField(primary_key=True)
    source = models.IntegerField(null=False)
    target = models.IntegerField(null=False)

class Graph_Node(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(null=False)
    user_name = models.CharField(max_length=30, null=False)
    community = models.IntegerField(null=False) """