# Packages and modules
import os
import re
import json
import pandas as pd
from ast import literal_eval
import unicodedata
import emoji
from emoji.unicode_codes import UNICODE_EMOJI

from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from nltk.stem import WordNetLemmatizer,PorterStemmer 
stop_words = stopwords.words('english')
stop_words.extend(['switzerland']) #'geneva','zurich','day','basel', ...

import gensim
import gensim.corpora as corpora
from gensim.models import CoherenceModel



# Further Processing for LDA
# input: clean dataframe
# output: list of word lists i.e.[[],[],...]
def word_to_list(data):
    # print('input is {}'.format(data.head()))
    # Tokenize to list
    word_list = []
    word_list += [word_tokenize(sentence) for sentence in data]

    # remove stop words    
    data_no_stop = [[word for word in line if word not in stop_words] for line in word_list]

    # lemmatize and remove blank list
    lemmatizer = WordNetLemmatizer() 
    lemmatized_words = [[lemmatizer.lemmatize(word) for word in line if word.isalpha()]for line in data_no_stop]

   #might generate meaningless term: e.g. stormy --> stormi
    return lemmatized_words,data_no_stop




def find_dominant_topic(ldamodel, corpus, text_list):
    dom_topic = pd.DataFrame()

    # Get main topic in each document
    for i, row_list in enumerate(ldamodel[corpus]):
        row = row_list[0] if ldamodel.per_word_topics else row_list  
        row = sorted(row, key=lambda x: (x[1]), reverse=True)
        # Get the Dominant topic, Perc Contribution and Keywords for each document
        for j, (topic_num, prop_topic) in enumerate(row):
            if j == 0:  # => dominant topic
                wp = ldamodel.show_topic(topic_num)
                topic_keywords = ", ".join([word for word, prop in wp])
                dom_topic = dom_topic.append(pd.Series([int(topic_num), round(prop_topic,4), topic_keywords]), ignore_index=True)
            else:
                break
    dom_topic.columns = ['Dominant_Topic', 'Topic_Percentage_Contribution', 'Topic_Keywords']

    return dom_topic[['Dominant_Topic', 'Topic_Percentage_Contribution']]




# Implement Gensim LDA
# input: word list, number of topics, number of words per topic
# output: lda model, dominant_topic_df, coherence, perplexity score
def gensim_lda(word_list,n_topic=10,n_word=20):
    # Creatw the term dictionary of courpus, where every unique term is assigned an index
    lda_path = './gensim_lda/'
    if not os.path.isdir(lda_path):
        os.mkdir(lda_path)
    dictionary = corpora.Dictionary(word_list)
    # dictionary.save(os.path.join(lda_path, 'dictionary.dict'))
    if len(dictionary) == 0:
        return False
    # Create a document-word matrix based on the dictionary
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in word_list]
    corpora.MmCorpus.serialize(os.path.join(lda_path+'corpus.mm'), doc_term_matrix)

    # generate and save LDA model
    Lda = gensim.models.ldamodel.LdaModel
    
    ldamodel = Lda(doc_term_matrix, num_topics=n_topic, id2word = dictionary, passes=50)
    topic_dom = find_dominant_topic(ldamodel, doc_term_matrix, word_list)

    return ldamodel, topic_dom



def save_topic(tw_list):
    result = []
    for item in tw_list:
        for k in range(len(item['pairs'])):
            row = []
            row.append('topic{}'.format(item['topic']))
            row.append('term{}'.format(k))
            row.append(item['pairs'][k][1])
            row.append(item['pairs'][k][0])
            result.append(row)

    result_df = pd.DataFrame(result,columns=['group','variable','prob','text'])
    result = result_df.to_json(orient="records")
    
    return json.loads(result)


def model2json(model,num_topics=4):
    topic_list = []
    for t in range(num_topics):
        t_dict = {}
        t_dict["topic"] = t
        t_dict["pairs"] = model.show_topic(t)
        topic_list.append(t_dict)
    jsonData = save_topic(topic_list)
    return jsonData



def lda_process(raw_text_list, num_topics = 4, num_words = 10):
    lem, dlist = word_to_list(raw_text_list) 
    print('\nlem: ', lem)
    if lem != []:
        ldamodel, topic_dom_df = gensim_lda(lem,n_topic=num_topics,n_word=num_words)
        if ldamodel:
            topicData = model2json(ldamodel)
            return topicData, topic_dom_df 
    # error occurs
    return False, False


