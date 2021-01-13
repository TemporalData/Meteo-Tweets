import pandas as pd
import numpy as np
import re
from operator import itemgetter
from scipy import stats
import networkx as nx
import igraph as ig
import json
import ast
import os
from networkx.algorithms import bipartite

# def main():
#     start = '2016-05-27 00:00:00'
#     end = '2016-06-02 23:59:59'
#     filename = '/static/js/week2016_sub.json'
#     generate_json(start,end,filename)

def generate_json(start,end,filename):
    current_dir = os.path.abspath(os.getcwd())
    filedir = current_dir+'/data/'
    file1 = os.path.join(filedir,'partial_net.csv')
    file2 =os.path.join(filedir,'allevents.csv')

    twitter_df = load_dataset(file1)
    sample_df = generate_sample_df(start, end, twitter_df)
    network_df = generate_network_df(sample_df)
    events_df = generate_events_df(file2, network_df)

    # generate user network
    G = generate_user_network(network_df)
    G = add_degree(G)
    sub_b = get_largest(G)
    G = community_detection(G)


    B, T, U = generate_bipartite(events_df)
    bi_sub_b = get_largest(B)
    U = community_detection(U)
    if filename == 'users':
        JSON_output(current_dir+'/text/static/js/users.json', sub_b)
    # JSON_output('bi_sample_data.json', B)
    # JSON_output('bi_term_data.json', T)
    # JSON_output('bi_user_data.json', U)
    if filename == 'bipartite':
        JSON_output(current_dir+'/text/static/js/bipartite.json', bi_sub_b)
# Load Dataset
def load_dataset(file1):
    twitter_df = pd.read_csv(file1, encoding='ISO-8859-15')
    return twitter_df

def generate_sample_df(start, end, twitter_df):
    # twitter_df['created_at_CET'] = twitter_df['created_at_CET']
    sample_df = twitter_df.loc[(twitter_df['created_at_CET']>=start) & (twitter_df['created_at_CET']<=end), ]

    return sample_df

# Extract 'user_mentions_id' and 'user_mentions_screen_name' from 'user_mentions'
def get_user_mentions(yi):
    if yi != '[]':
        yi2 = yi.split('}')
        yi2.pop()
    
        res = []
        scr = []
        res.append(yi2[0].split(',')[3])
        scr.append(yi2[0].split(',')[4].split("'")[-2])
    
        for i in yi2[1:]:
            tmp = i.split(',')
            res.append(tmp[4])
            scr.append(tmp[5].split("'")[-2])
        res = [int(''.join(re.findall("\d+",j))) for j in res]
        
        return(res, scr)
    else:
        return(None, None)

# Extract hashtags
def get_hashtags(yi):
    if yi != '[]':
        yi2 = yi.split('}')
        yi2.pop()
    
        scr = []
        scr.append(yi2[0].split(',')[2].split("'")[-2])
    
        for i in yi2[1:]:
            tmp = i.split(',')
            scr.append(tmp[3].split("'")[-2])
        
        return(scr)
    else:
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
    network_df = pd.DataFrame(columns = ['created_at_CET', 'place_full_name', 'user_screen_name', 'id', 'text', 'retweet_count', 'favorite_count', 
                                     'is_retweet', 'is_favorite', 'is_quote', 'is_reply', 'quoted_status_id_permalink', 
                                     'in_reply_to_status_id', 'in_reply_to_user_id', 'in_reply_to_screen_name', 
                                     'user_id', 'n_user_mentions', 'user_mentions_id', 'user_mentions_screen_name', 'hashtags_name', 
                                     'user_followers_count', 'user_following_count', 'user_favourited_other_tweets_count', 'tweet_group', 'tweet_weight'])
  
    # columns with same values
    same_columns = ['created_at_CET', 'place_full_name', 'user_screen_name', 'id', 'text', 'retweet_count', 'favorite_count', 
                'is_retweet', 'is_favorite', 'is_quote', 'is_reply', 'quoted_status_id_permalink', 
                'in_reply_to_status_id', 'in_reply_to_user_id', 'in_reply_to_screen_name', 
                'user_id', 'n_user_mentions', 
                'user_followers_count', 'user_following_count', 'user_favourited_other_tweets_count']
    network_df[same_columns] = sample_df[same_columns]

    # extract 'user_mentions_id' and 'user_mentions_screen_name' from 'user_mentions'
    # number of users in the sample dataset
    user_id_list = sample_df.user_id.unique().tolist()
    # len(user_id_list)

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

# get interactions between different users
# the function iterates over the dataframe, obtain the id and screen_name of the user that the author of that specific tweet reply or mention
# it returns the author of the specific tweet together with a list of users with whom the user interacted
def get_interactions(row):
    # from every row of the dataframe
    # obtain 'user_id' and 'user_screen_name'
    user = row['user_id'], row['user_screen_name'] #, row['user_followers_count']
    # if there is no user id
    if user[0] is None:
        return (None, None), []
    
    # the interactions are a set of tuples
    interactions = set()
    
    # add all interactions 
    # add the interactions with replies
    interactions.add((row['in_reply_to_user_id'], row['in_reply_to_screen_name']))
    # add the interactions with user mentions
    if row['user_mentions_id'] is not None:
        for i in range(len(row['user_mentions_id'])):
            interactions.add((row['user_mentions_id'][i], row['user_mentions_screen_name'][i]))
    
    # interactions.add((row['retweeted_id], row['retweeted_screen_name']))
    
    # discard if user id is in interactions
    interactions.discard((row['user_id'], row['user_screen_name']))
    # discard all not existing values
    interactions.discard((None, None))
    
    # return user and interactions
    return user, interactions

def generate_user_network(network_df):
    # build directed network
    G = nx.DiGraph()
    # populate the Graph by calling the function get_interactions
    for index, tweet in network_df.iterrows():
        user, interactions = get_interactions(tweet)
        user_id, user_name = user
        tweet_id = tweet['id']
        tweet_group = tweet['tweet_group']
        tweet_weight = tweet['tweet_weight']
        text = tweet['text'] 

        for interaction in interactions:
            int_id, int_name = interaction
            G.add_edge(user_id, int_id, tweet_id=tweet_id, tweet_group=tweet_group,edge_weight=tweet_weight, text=text)
        
            G.nodes[user_id]['name'] = user_name
            G.nodes[user_id]['node_weight'] = tweet['user_followers_count']
            G.nodes[int_id]['name'] = int_name
            G.nodes[int_id]['node_weight'] = tweet['user_followers_count']
    return(G)

def add_degree(G):
    degree_list = [val for (node, val) in G.degree()]
    node_list = list(G.nodes())
    degree_dict = {k:v for k,v in zip(node_list, degree_list)}
    nx.set_node_attributes(G, degree_dict, 'degree')
    return(G)

def get_largest(G):
    if bipartite.is_bipartite(G):
        largest_component = max(nx.connected_components(G), key=len)     
    else:
        # weakly_connected_components: for large size of network
        largest_component = max(nx.weakly_connected_components(G), key=len)
    sub = G.subgraph(largest_component) 
    return(sub)  

def generate_events_df(file2, network_df):
    network_df.reset_index(level=0, inplace=True)

    events_df = pd.read_csv(file2)
    events_df = events_df[events_df.astype(str)['doc_list'] != '[]']
    
    events_df['doc_list'] = events_df.doc_list.apply(lambda s: list(ast.literal_eval(s)))
    events_df = events_df.explode('doc_list').reset_index(drop=True)
    events_df = pd.merge(events_df, network_df, how='inner', left_on='doc_list', right_on='index')
    events_df['weight'] = events_df.groupby(['terms','user_id'])['id'].transform('count')

    return events_df

def generate_bipartite(events_df):
    B = nx.Graph()
    B.add_nodes_from(events_df['terms'], bipartite=0)
    B.add_nodes_from(events_df['user_id'], bipartite=1)
    B.add_weighted_edges_from(
        [(row['terms'], row['user_id'], row['weight']) for idx, row in events_df.iterrows()])

    degree_list = [val for (node, val) in B.degree()]
    node_list = list(B.nodes())
    degree_dict = {k:v for k,v in zip(node_list, degree_list)}

    nx.set_node_attributes(B, degree_dict, 'degree')

    term_nodes = {n for n, d in B.nodes(data=True) if d["bipartite"] == 0}
    user_nodes = set(B) - term_nodes
    T = bipartite.weighted_projected_graph(B, term_nodes)
    U = bipartite.weighted_projected_graph(B, user_nodes)
    return(B, T, U)

def community_detection(U):
    # convert network from networkx to igraph
    U2 = ig.Graph.TupleList(U.edges(), directed=True)
    communities = U2.community_infomap()
    membership  = communities.membership
    node_list = list(U.nodes())
    community_dict = {k:v for k,v in zip(node_list, membership)}   
    nx.set_node_attributes(U, community_dict, 'community')
    return(U)

def JSON_output(file_name, network_data):
    JSON_data = nx.node_link_data(network_data)
    with open(file_name, 'w') as outfile:
        json.dump(JSON_data, outfile)

# if __name__ == "__main__":
#     main()
