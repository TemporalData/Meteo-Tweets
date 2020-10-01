# 
# import packages and modules
import os
import re
import numpy as np
import pandas as pd
from ast import literal_eval
import unicodedata
from wordcloud import WordCloud
import emoji
from emoji.unicode_codes import UNICODE_EMOJI

from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from nltk.stem import WordNetLemmatizer,PorterStemmer 
stop_words = stopwords.words('english')
stop_words.extend(['switzerland']) #'geneva','zurich','day','basel', ...

# import matplotlib.pyplot as plt
# import seaborn as sns
# sns.set_style('whitegrid')
# %matplotlib inline

from time import time
# import warnings
# warnings.filterwarnings("ignore",category=DeprecationWarning)
# warnings.simplefilter("ignore", DeprecationWarning)

import gensim
import gensim.corpora as corpora
from gensim.models import CoherenceModel
from gensim.summarization import keywords
from gensim.models import LdaModel

import gensim
# import pyLDAvis.gensim
# pyLDAvis.enable_notebook()
from gensim.models import CoherenceModel

from datetime import date

import hdbscan

# from bokeh.layouts import column, row
# from bokeh.models import CustomJS, Slider,DateRangeSlider
# from bokeh.plotting import ColumnDataSource, figure, output_file, show


def main():
    start = '2016-07-01'
    end = '2016-07-07'
    pipeline(start, end, path)


# Load Dataset
# input: pre-filtered csv file
# output: dataframe read from the file
def load(file='partial.csv'):
    raw = pd.read_csv(file, engine='python',encoding='latin_1') #,encoding='latin_1'
    # raw = raw.rename(columns={'Unnamed: 0': 'doc_no'}) # rename original indices
    # raw = raw[raw.lang == 'en'] # keep English only
    return raw



# Text Cleaning
# input: data after hdbscan, cluster_id
# less records, faster processing
# output: clean data
def clean(temp,isdate=False,start='2016-07-01',end='2016-07-08'):
    if isdate == True:
        temp = temp.loc[(temp.date >= start)&(temp.date <= end)]
    # print('selectd data is \n'.format(temp.head()))

    # temp.reset_index(drop=True,inplace=True)
    # remove links starting with "http(s)"
    temp['text'] = temp['text'].str.split("http", n = 1, expand = True)[0] 
    
    # remove punctuations, normalize to lowercase, delete default text
    temp['text'] = temp['text'].map(lambda x: re.sub('[,\.!?\@]', ' ', x))
    temp['text'] = temp['text'].map(lambda x: re.sub('\r\n', ' ', x))
    temp['text'] = temp['text'].map(lambda x: x.lower()) 
    
    # remove default text "Just posted a photo/video"
    temp['text'] = temp['text'].str.replace('just posted a photo', '')
    temp['text'] = temp['text'].str.replace('just posted a video', '')

    # recognizable unicode format
    temp['text'] = temp['text'].str.replace(r'<u\+',r'\\u') 
    temp['text'] = temp['text'].str.replace('>','') 
    temp['text'] = temp['text'].map(lambda x: re.sub("(?:u0001)|(?:u000e)", "U0001", x))

    # demojize emoji unicode to text
    temp['text'] = temp['text'].str.rstrip('\\') #remove distracting "\" at the end of strings
    temp['text'] = temp['text'].map(lambda x: emoji.demojize(bytes(x,encoding='latin_1').decode('unicode_escape')))
    temp['text'] = temp['text'].map(lambda x: re.sub('[:\#]', ' ', x)) #remove new ":" from demojize
    temp['text'] = temp['text'].map(lambda x: x.lower()) 
# doc_no,user_screen_name,latitude,longitude,text,created_at_CET,date,text_processed
    temp = temp[['doc_no','user_screen_name','latitude','longitude','date','text']]
    # print('clean data is \n'.format(temp.head()))
    return temp





# Define a timeline slider
# granularity: day / week?
# return a time range with start and end
# def callback(attr, old, new):
        
#     start_date = date.fromtimestamp(new[0]/1000)
#     end_date = date.fromtimestamp(new[1]/1000)

#     # update columndatasource
#     source.data = dict(longitude=dev_merc_coord[0], latitude=dev_merc_coord[1])
#     update_all(start_date,end_date)


# def date_selection():    
#     date_slider = DateRangeSlider(title="Date Range: ", start=date(2015, 1, 1),
#                                  end=date(2018,9,6), value=(date(2015, 1, 1), date(2015, 12, 31)), step=1)
    
#     date_slider.on_change('value', callback)


# Apply HDBSCAN on the dataset
# input: dataframe, start time, end time
# other params(maybe by sliders): min_cluster_size, min_samples, eps, alpha, gen_min_span_tree
# output: cluster model, new dataframe with cluster_id
def do_hdbscan(data, ts='2016-07-01',te='2016-07-08',min_cluster_size=5,min_samples=5):
    location = data[['latitude','longitude']]
    location = location.values.tolist()
    clusterer = hdbscan.HDBSCAN(min_cluster_size=5, min_samples=5, gen_min_span_tree=True)
    clusterer.fit(location)
    label = clusterer.labels_
    data['cluster_id'] = label.tolist()  
    data.reset_index(inplace=True)
    # print('cluster_Data is '.format(data[['doc_no']].head()))
    return clusterer, data

# def vis_hdbscan(cluster):
#     clusterer.minimum_spanning_tree_.plot(edge_cmap='viridis',
#                                       edge_alpha=0.6,
#                                       node_size=80,
#                                       edge_linewidth=2,
#                                      )




# Further Processing for LDA
# input: clean dataframe
# output: list of word lists i.e.[[],[],...]
def word_to_list(data):
    # print('input is {}'.format(data.head()))
    # Tokenize to list
    word_list = []
    word_list += [word_tokenize(sentence) for sentence in data['text'].values.tolist()]

    # remove stop words    
    data_no_stop = [[word for word in line if word not in stop_words] for line in word_list]


    # lemmatize and remove blank list
    lemmatizer = WordNetLemmatizer() 
    lemmatized_words = [[lemmatizer.lemmatize(word) for word in line if word.isalpha()]for line in data_no_stop]

    stemmer = PorterStemmer()
    stem_words = [[stemmer.stem(word) for word in line if word.isalpha()] for line in data_no_stop]
    #might generate meaningless term: e.g. stormy --> stormi
    return lemmatized_words,stem_words


# Searching weather-relaetd terms in each tweet and build an index to doc_idx
# input: lemmatized list of lists of words, in order of doc_idx
# output: dataframe['weather_terms','doc_list']
def find_weather_event(filename, lem_data, idx2doc):
    weather_dict = {}
    event_list = pd.read_csv(filename)
    event_list = event_list.terms.map(lambda x: x.lower()).values.tolist()
    event_list.append('thunderstorm')
    for event in event_list:
        weather_dict[event] = []

    for i in range(len(lem_data)):
        for word in lem_data[i]:
            if word in event_list:
                weather_dict[word].append(idx2doc.iloc[i])


    event_df = pd.DataFrame([{'terms':term, 'doc_list': doc_list} for term,doc_list in weather_dict.items()])
    return event_df


# Show wordcloud 
# input: list of word lists i.e.[[],[],...], number of words to show
# output: image
# def wordcloud(data_list,word_no=300): 
#     weather_list = pd.read_csv('weather_dict.csv',engine='python').map(lambda x: x.lower()).values.tolist()
#     input_str =','.join(','.join(row) for row in data_list)
#     wordcloud = WordCloud(background_color='white', width = 1000, height= 600, max_words=word_no, contour_width=3) 
#     wordcloud.generate(input_str)
#     w_cloud = wordcloud.to_image() #PIL.Image.Image object
#     # wordcloud.to_file('wordcloud'+str(word_no)+'.png')
#     return w_cloud



# Implement Gensim LDA
# input: word list, number of topics, number of words per topic
# output: lda model, dominant_topic_df, coherence, perplexity score
def gensim_lda(word_list,n_topic=10,n_word=20):
    # Creatw the term dictionary of courpus, where every unique term is assigned an index
    lda_path = './gensim_lda/'
    if not os.path.isdir(lda_path):
        os.makedirs (lda_path)
    dictionary = corpora.Dictionary(word_list)
    # dictionary.save(os.path.join(lda_path+'dictionary.dict'))

    # Create a document-word matrix based on the dictionary
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in word_list]
    corpora.MmCorpus.serialize(os.path.join(lda_path+'corpus.mm'), doc_term_matrix)

    # generate and save LDA model
    model_name = lda_path+'topic'+str(n_topic)+'.model'
    Lda = gensim.models.ldamodel.LdaModel
    ldamodel = Lda(doc_term_matrix, num_topics=n_topic, id2word = dictionary, passes=50)
    ldamodel.save(model_name)

    # Print out topic no. and corresponding keywords, default num_words=10
    # for i in ldamodel.print_topics(num_words=n_word): 
    #     for j in i: 
    #         print (j)

    # prepare lda visualization
    # model_data = pyLDAvis.gensim.prepare(ldamodel, doc_term_matrix, dictionary)
    # pyLDAvis.save_html(model_data,lda_path+'g_lda'+str(num_t)+'.html')
    # pyLDAvis.show(model_data)


    # Compute performance metrics
    # Coherence Score:  0.4 low, 0.5 ok, 0.56 fair
    coherence_model_lda = CoherenceModel(model=ldamodel, texts=word_list, dictionary=dictionary, coherence='c_v') 
    coherence = coherence_model_lda.get_coherence() 
    perplexity = ldamodel.log_perplexity(doc_term_matrix)

    # Find the dominant topic
    dominant_topic = []
    for i,line in enumerate(ldamodel[doc_term_matrix]): 
        line = sorted(line, key=lambda x: (x[1]),reverse = True) #rank topic probabilities in descending order
        (topic_no, topic_prob) = line[0] #dominant topic with highest probability
        dominant_topic.append([int(topic_no), round(topic_prob,4)])
        dominant_topic_df = pd.DataFrame(dominant_topic,columns=['dom_topic','dom_prob'])


    return ldamodel, dominant_topic_df, coherence, perplexity

# Find the most representative topic in a region/cluster;
# Way 1: topic with the highest ratio from LDA
# Way 2: LDA --> dominant topic per tweet --> count the most frequent dom_tpc
def find_region_topic(c_data,c_id):

    # if c_id == -1:

    temp = c_data[c_data.label == c_id]
    temp = clean(temp)
    temp_list = word_to_list(temp)
    # temp_wordcloud = wordcloud(temp_list,300) 
    lda_model, dom_top_data, co_score, pe_score= gensim_lda(temp_list)



#input: lda.print_topics string [(0, '0.057*"repost" + ...')]
def topic_kw_pair(text): 
    top_list = []
    for pair in text:
        top_js = {'topic': pair[0],'pairs':[]}
        st= re.split('[* + "]',pair[1])
        st = [i for i in st if len(i)>0]
        for i in range(len(st)//2):
            top_js['pairs'].append((st[2*i],st[2*i+1]))
        top_list.append(top_js)

    return top_list


def save_topic(tw_list,filepath):
    result = []
    for item in tw_list:
        for k in range(len(item['pairs'])):
            row = []
            row.append('topic{}'.format(item['topic']))
            row.append('term{}'.format(k))
            row.append(item['pairs'][k][0])
            row.append(item['pairs'][k][1])
            result.append(row)

    result_df = pd.DataFrame(result,columns=['group','variable','prob','text'])
    result_df.to_csv(filepath+'topics.csv',index=False)
    max_prob = result_df['prob'].values.max()
    min_prob = result_df['prob'].values.min()
    return result, max_prob, min_prob





def _clear_old_files(fpath, flist):
    files = os.listdir(fpath)
    for name in flist:
        if name in files:
            os.remove(os.path.join(fpath,name))





def pipeline(start, end,filepath):

    # filename = 'complete_swiss_dataset.csv'
    # prefilter(filename)

    dataset = 'partial.csv'
    docfile = 'documents.csv'
    clufile = 'clusters.csv'
    # weafile = 'weather_terms.csv'
    eventfile = 'events.csv'
    fullweafile = 'new_weather.csv'
    
    _clear_old_files(filepath, [docfile,clufile,eventfile])

    raw_data = load(filepath+dataset)
    target_data = clean(temp=raw_data,isdate=True, start=start,end=end)

    # 1) clustered_data has exactly same fields ordered as in Document model
    cluster_model, clustered_data = do_hdbscan(data=target_data,ts=start,te=end)
    clustered_data.to_csv(filepath+docfile, index=False)


    # 2) find weather terms mentioned in each doc and save a list of index
    lem_data,stem_data = word_to_list(clustered_data)
    # lem_data,stem_data = word_to_list(target_data)
    # idx2doc = target_data['doc_no']
    idx2doc = clustered_data['doc_no']
    weather_event = find_weather_event(filepath+fullweafile,lem_data,idx2doc)
    weather_event.to_csv(filepath+eventfile,index=False)
    # weather_event.to_csv(filepath+weafile,index=False)


    # selected cluster_id can be return by vis interface
    # e.g. bubble map in d3


    # desc_cluster_id = clustered_data.groupby(''cluster_id'').count().sort_values('doc_no',ascending=False).index# -1: noise
    # cluster_id = desc_cluster_id[0] if desc_cluster_id[0] != -1 else desc_cluster_id[1]
    
    # dom_top = find_region_topic(clustered_data,cluster_id)


    # date_slider = DateRangeSlider(title="Date Range: ", start=date(2015, 1, 1),
    #                             end=date(2018,9,6), value=(date(2015, 1, 1), date(2015, 12, 31)), step=7)
    # date_slider.on_change('value', callback)
    # layout = column(date_slider)
    # show(layout)

def event_pipeline(eventname, filepath):
    event_mild = pd.read_csv(filepath+'new_mild.csv')
    event_severe = pd.read_csv(filepath+'new_severe.csv')
    full_event_df = pd.concat([event_mild,event_severe])
    
    doc_list = literal_eval(full_event_df[full_event_df.event == eventname]['doc_list'].values[0])

    raw_df = load(filepath+'partial.csv')
    raw_doc_df = raw_df[raw_df.doc_no.isin(doc_list)]
    target = clean(temp=raw_doc_df)
    lem_data,stem_data = word_to_list(target)
    ldamodel, dominant_topic_df, coherence, perplexity = gensim_lda(lem_data,n_topic=4,n_word=15)

    return ldamodel.print_topics() #[(0,str),(1,str)] = show_topic(top_id)

if __name__ == "__main__":
    main()




    





    



 
 









