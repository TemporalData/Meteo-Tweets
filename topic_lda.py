#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import re
import numpy as np
import pandas as pd
import unicodedata
from wordcloud import WordCloud
import emoji
from emoji.unicode_codes import UNICODE_EMOJI


# In[2]:


import nltk
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from nltk.stem import WordNetLemmatizer 
stop_words = stopwords.words('english')
stop_words.extend(['switzerland']) #'geneva','zurich','day','basel', ...


# In[3]:


import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')
get_ipython().run_line_magic('matplotlib', 'inline')


# In[4]:


from time import time
import seaborn as sns
import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)
warnings.simplefilter("ignore", DeprecationWarning)


# In[5]:


import gensim
import gensim.corpora as corpora
from gensim.models import CoherenceModel
from gensim.summarization import keywords
from gensim.models import LdaModel

import pyLDAvis.gensim
import gensim
pyLDAvis.enable_notebook()


# In[6]:


# from pyLDAvis import sklearn as sklearn_lda
# import pickle 
# import pyLDAvis

# # Load the LDA model from sk-learn
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.decomposition import LatentDirichletAllocation as LDA


# Ref:
# 
# >[LDA gensim](https://radimrehurek.com/gensim/models/ldamodel.html)
# 
# >[NLTK raw text](http://www.nltk.org/book/ch03.html)
# 
# 
# 
# >[pyLDAvis]( https://pyldavis.readthedocs.io/en/latest/modules/API.html), [paper](https://www.aclweb.org/anthology/W14-3110.pdf)
# 
# >[Full emoji unicode list]( https://unicode.org/emoji/charts/full-emoji-list.html#1f60f)
# 
# 
# 

# # Pre-filter Relevant Attributes 
# Or download <i><b>partial.csv</b></i> directly

# In[6]:


file = 'complete_swiss_dataset.csv'
# use this block if you generate new dataset locally
full_data = pd.read_csv(file,engine='python',encoding='latin_1')
partial_data = full_data[['user_screen_name', 'latitude', 'longitude', 'text', 'lang', 'created_at_CET']]

# split datetime to date
test = partial_data['created_at_CET']
test = pd.DataFrame(test.str.split(' ', n = 1, expand = True)[0].tolist(), columns=['date'])
partial_data = pd.concat([partial_data, test], axis=1, sort=False)

# save partial data
partial_data.to_csv('partial.csv')


# # Load Dataset

# In[7]:


fn = 'partial.csv'
raw = pd.read_csv(fn, engine='python')
raw = raw.rename(columns={'Unnamed: 0': 'doc_no'}) # original tweet indices
raw = raw[raw.lang == 'en'] # keep English only
raw.head()
# raw.count() #420330


# In[10]:


# t1, t2 can be acquired from timeline given the granularity
t1 = '2016-06-01'
t2 = '2016-07-01'
papers = raw.loc[(raw['date']>=t1)& (raw['date']<t2)]


# # Clean Text

# In[11]:


# provide the duration of time, faster processing
# remove default text "Just posted a photo/video"
# remove links starting with "http(s)"
# translate unicode emojis to plain text

 
papers['text_processed'] = papers['text'].str.split("http", n = 1, expand = True)[0] 
# papers.count() #27487

# remove punctuations, normalize to lowercase, delete default text
papers['text_processed'] = papers['text_processed'].map(lambda x: re.sub('[,\.!?\@]', ' ', x))
papers['text_processed'] = papers['text_processed'].map(lambda x: re.sub('\r\n', ' ', x))
papers['text_processed'] = papers['text_processed'].map(lambda x: x.lower()) 
papers['text_processed'] = papers['text_processed'].str.replace('just posted a photo', '')
papers['text_processed'] = papers['text_processed'].str.replace('just posted a video', '')

# recognizable unicode format
papers['text_processed'] = papers['text_processed'].str.replace(r'<u\+',r'\u') 
papers['text_processed'] = papers['text_processed'].str.replace('>','') 
papers['text_processed'] = papers['text_processed'].map(lambda x: re.sub("(?:u0001)|(?:u000e)", "U0001", x))

# demojize emoji unicode to text
papers['text_processed'] = papers['text_processed'].str.rstrip('\\') #remove distracting "\" at the end of strings
papers['text_processed'] = papers['text_processed'].map(lambda x: emoji.demojize(bytes(x,encoding='latin_1').decode('unicode_escape')))
papers['text_processed'] = papers['text_processed'].map(lambda x: re.sub('[:\#]', ' ', x)) #remove new ":" from demojize
papers['text_processed'] = papers['text_processed'].map(lambda x: x.lower()) 


# In[32]:


papers['text_processed'].head(20)


# In[13]:


# Tokenize to list
word_list = []
word_list += [word_tokenize(sentence) for sentence in list(papers['text_processed'].values)]

# remove stop words    
data_no_stop = [[word for word in line if word not in stop_words] for line in word_list]

# lemmatize and remove blank list
lemmatizer = WordNetLemmatizer() 
data_lemmatized = [[lemmatizer.lemmatize(word) for word in line if word.isalpha()]for line in data_no_stop]


# # Wordcloud

# In[19]:


# Wordcloud visualization
# convert lists of words to a long string
input_str =','.join(','.join(row) for row in data_lemmatized)
wordcloud = WordCloud(background_color='white', width = 1000, height= 600, max_words=300, contour_width=3) 
wordcloud.generate(input_str)
wordcloud.to_image()


# In[ ]:


# # Save word cloud pic 
# wordcloud.to_file('wordcloud.png')


# # Gensim LDA

# In[33]:


# Create the term dictionary, where every unique term is assigned an index. 
lda_path = './gensim_lda/'
dictionary = corpora.Dictionary(data_lemmatized)
dictionary.save(os.path.join(lda_path+'dictionary.dict'))


# In[34]:


# Create a document-word matrix based on the dictionary
doc_term_matrix = [dictionary.doc2bow(doc) for doc in data_lemmatized]
corpora.MmCorpus.serialize(os.path.join(lda_path+'corpus.mm'), doc_term_matrix)

print (len(doc_term_matrix))
print (doc_term_matrix[100])


# In[37]:


# desired topic numbers 
num_t = 20
model_name = lda_path+'topic'+str(num_t)+'.model'


# In[39]:


# Apply LDA model with gensim
start = time()
Lda = gensim.models.ldamodel.LdaModel
ldamodel = Lda(doc_term_matrix, num_topics=num_t, id2word = dictionary, passes=50)
print ('used time: {:.2f}s'.format(time()-start))

ldamodel.save(model_name)


# In[41]:


# Print out topic no. and corresponding keywords, default num_words=10
for i in ldamodel.print_topics(num_words=20): 
    for j in i: 
        print (j)


# In[152]:


# # Load pervious parameters

# dictionary = gensim.corpora.Dictionary.load('dictionary.dict')
# doc_term_matrix = gensim.corpora.MmCorpus('corpus.mm') #doc_term_matrix
# ldamodel = gensim.models.LdaModel.load(model_name)


# In[42]:


# Prepare for visualization 

data = pyLDAvis.gensim.prepare(ldamodel, doc_term_matrix, dictionary)
pyLDAvis.save_html(data,lda_path+'g_lda'+str(num_t)+'.html')
pyLDAvis.show(data)


# # Performance Metrics

# In[43]:


from gensim.models import CoherenceModel


# In[44]:


lda = gensim.models.LdaModel.load(model_name)
coherence_model_lda = CoherenceModel(model=lda, texts=data_lemmatized, dictionary=dictionary, coherence='c_v') 
#Coherence Score:  0.4430156773723783 (num_t=10, low)
#Coherence Score:  0.5086680966615635 (num_t=50, ok)
#Coherence Score:  0.5624528283697039 (30, fair)
coherence_lda = coherence_model_lda.get_coherence() 
print('\nCoherence Score: ', coherence_lda)
print('\nPerplexity: ', lda.log_perplexity(doc_term_matrix))


# # Find Dominant Topic

# In[46]:


def dom_topic_per_doc(lda=ldamodel,dt_mat=doc_term_matrix):
    dominant_topic = []
    for i,line in enumerate(lda[dt_mat]): # for each tweet
        line = sorted(line, key=lambda x: (x[1]),reverse = True) #rank topic probabilities in descending order
        (topic_no, topic_prob) = line[0] #dominant topic with highest probability
        dominant_topic.append([int(topic_no), round(topic_prob,4)])
        dominant_topic_df = pd.DataFrame(dominant_topic,columns=['dom_topic','dom_prob'])
    return dominant_topic_df


# In[48]:


x = dom_topic_per_doc(ldamodel, doc_term_matrix)
x.head()


# In[50]:


papers.reset_index(drop=True,inplace=True)
papers.head()


# In[51]:


papers = pd.concat([papers, x], axis=1)
papers.head()


# In[52]:


# papers.to_csv('topic_partial.csv')

