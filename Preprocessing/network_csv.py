import pandas as pd
import numpy as np
import re
import os
from ast import literal_eval

def main():
    current_dir = os.path.abspath(os.path.join(os.getcwd(),'..'))
    filedir = current_dir+'/static/data/'
    file1 = os.path.join(filedir,'complete_swiss_dataset.csv')
    file2 =os.path.join(filedir,'allevents.csv')

    twitter_df = load_dataset(file1)
    sample_df = generate_sample_df(twitter_df)

    network_df = generate_network_df(sample_df)
    output_file1 = os.path.join(filedir,'users_network.csv')
    network_df.to_csv(output_file1, index = False)

    events_df = generate_events_df(file2, network_df)
    output_file2 = os.path.join(filedir,'events_network.csv')
    events_df.to_csv(output_file2, index = False)

# Load dataset
def load_dataset(file1):
    twitter_df = pd.read_csv(file1, encoding='ISO-8859-15')
    return twitter_df

# Get English tweets
def generate_sample_df(twitter_df):
    sample_df = twitter_df.loc[(twitter_df['lang']=='en'), ]
    return sample_df

# Extract 'user_mentions_id' and 'user_mentions_screen_name' from 'user_mentions'
def get_user_mentions(yi):
    id = []
    name = []
    try: 
        yi = literal_eval(yi)
        if len(yi)>0:
            for i in range(len(yi)):
                id.append(yi[i]['id_str'])
                name.append(yi[i]['screen_name'])
        #print(id,name)
        return(id,name)
    except:
        return(None,None)

# Extract hashtags
def get_hashtags(yi):
    hashtag = []
    try: 
        yi = literal_eval(yi)
        if len(yi)>0:
            for i in range(len(yi)):
                hashtag.append(yi[i]['text'])
        #print(hashtag)
        return(hashtag)
    except:
        return(None)

# Compute tweet groups and weights
# tweet group 0-no 1-is_reply, 2-has mentions(n_user_mentions>0), 3-both
def get_tweet_group(x):
    if x['is_reply'] == 0 and x['n_user_mentions'] == 0:
        return 0 
    elif x['is_reply'] == 1 and x['n_user_mentions'] == 0:
        return 1 # is reply
    elif x['is_reply'] == 0 and x['n_user_mentions'] > 0:
        return 2 # has user mentions
    else:
        return 3 # both

def generate_network_df(sample_df):
    # columns for social network analysis
    network_df = pd.DataFrame(columns = ['created_at_CET', 'place_full_name', 'latitude', 'longitude', 'user_screen_name', 'id', 'retweet_count', 'favorite_count', 
                                     'is_retweet', 'is_favorite', 'is_quote', 'is_reply', 'quoted_status_id_permalink', 
                                     'in_reply_to_status_id', 'in_reply_to_user_id', 'in_reply_to_screen_name', 
                                     'user_id', 'n_user_mentions', 'user_mentions_id', 'user_mentions_screen_name', 'hashtags_name', 
                                     'user_followers_count', 'user_following_count', 'user_favourited_other_tweets_count', 'tweet_group', 'tweet_weight'])
  
    # columns with same values
    same_columns = ['created_at_CET', 'place_full_name', 'latitude', 'longitude', 'user_screen_name', 'id', 'retweet_count', 'favorite_count', 
                'is_retweet', 'is_favorite', 'is_quote', 'is_reply', 'quoted_status_id_permalink', 
                'in_reply_to_status_id', 'in_reply_to_user_id', 'in_reply_to_screen_name', 
                'user_id', 'n_user_mentions',
                'user_followers_count', 'user_following_count', 'user_favourited_other_tweets_count']
    network_df[same_columns] = sample_df[same_columns]

    # extract 'user_mentions_id' and 'user_mentions_screen_name' from 'user_mentions'
    network_df['user_mentions_id'], network_df['user_mentions_screen_name'] = zip(*sample_df['user_mentions'].apply(get_user_mentions))

    # extract hashtags
    network_df['hashtags_name'] = sample_df['hashtags'].apply(get_hashtags)

    # compute tweet groups and weights
    network_df['tweet_group'] = sample_df.apply(get_tweet_group, axis=1)

    # tweet weight
    network_df['tweet_weight'] = sample_df['retweet_count'] + sample_df['favorite_count']
    
    # None values in the network
    network_df = network_df.where((pd.notnull(network_df)), None)

    return network_df

def generate_events_df(file2, network_df):
    network_df.reset_index(level=0, inplace=True)

    events_df = pd.read_csv(file2)
    events_df = events_df[events_df.astype(str)['doc_list'] != '[]']
    
    events_df['doc_list'] = events_df.doc_list.apply(lambda s: list(literal_eval(s)))
    events_df = events_df.explode('doc_list').reset_index(drop=True)
    events_df = pd.merge(events_df, network_df, how='inner', left_on='doc_list', right_on='index')
    events_df['weight'] = events_df.groupby(['terms','user_id'])['id'].transform('count')

    return events_df

if __name__ == "__main__":
    main()