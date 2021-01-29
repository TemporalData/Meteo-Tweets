# Packages and modules
import os
import re
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




# Dataset name and directories
FILE_DIR = os.path.join(os.getcwd(), 'data') # Directory to save output
DATAFILE = 'complete_swiss_dataset.csv' # Original dataset


# Text Cleaning
# input: data after hdbscan, cluster_id
# less records, faster processing
# output: clean data
def clean(temp,isdate=False,start='2015-01-01',end='2018-09-06'):
    if isdate == True:
        temp = temp.loc[(temp.date >= start)&(temp.date <= end)]
    # print('selectd data is \n'.format(temp.head()))

    # Remove index 
    temp.reset_index(drop=True,inplace=True)
    # remove links starting with "http(s)"
    temp['text'] = temp['text'].apply(lambda x: x.split("http")[0])
    
    # remove punctuations, normalize to lowercase, delete default text
    temp['text'] = temp['text'].apply(lambda x: re.sub('[,\.!?\@]', ' ', x))
    temp['text'] = temp['text'].apply(lambda x: re.sub('\r\n', ' ', x))
    temp['text'] = temp['text'].apply(lambda x: x.lower()) 
    
    # remove default text "Just posted a photo/video"
    temp['text'] = temp['text'].apply(lambda x: x.replace('just posted a photo', ''))
    temp['text'] = temp['text'].apply(lambda x: x.replace('just posted a video', ''))

    # recognizable unicode format
    temp['text'] = temp['text'].apply(lambda x: x.replace(r'<u+',r'\u') )
    temp['text'] = temp['text'].apply(lambda x: x.replace('>','') )
    temp['text'] = temp['text'].apply(lambda x: re.sub("(?:u0001)|(?:u000e)", "U0001", x))

    # demojize emoji unicode to text
    temp['text'] = temp['text'].apply(lambda x: x.rstrip('\\')) #remove distracting "\" at the end of strings
    temp['text'] = temp['text'].apply(lambda x: emoji.demojize(bytes(x,encoding='latin_1').decode('unicode_escape')))
    temp['text'] = temp['text'].apply(lambda x: re.sub('[:\#]', ' ', x)) #remove new ":" from demojize
    temp['text'] = temp['text'].apply(lambda x: x.lower()) 

    # extract date from datetime 
    temp['date'] = temp['created_at_CET'].apply(lambda x: x.split(' ')[0])
    temp = temp[['doc_no','user_screen_name','latitude','longitude','date','text']]
    # print('clean data is \n'.format(temp.head()))
    return temp




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

   #might generate meaningless term: e.g. stormy --> stormi
    return lemmatized_words,data_no_stop



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
    # ldamodel.save(model_name)

    return ldamodel




# Input: list of lists consist of term-prob pairs, 
# e.g. [[('swiss', 0.15638249),(...)],[],[],[]]
# Output: json files,  
# e.g. [{"group":"topic0","variable":"term0","prob":0.064,"text":"aurora"},{...}]
def save_topic(tw_list,filepath):
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
    # result_df.to_csv(filepath+'topics.csv',index=False)
    result_df.to_json(filepath,orient="records")



def _clear_old_files(fpath, flist):
    files = os.listdir(fpath)
    for name in flist:
        if name in files:
            os.remove(os.path.join(fpath,name))





# Read original data, slice columns, text propcessing, and save to new file
# input: filedir, filename
# output: partial-clean-term.csv ['user_screen_name', 'latitude', 'longitude', 'text', 'created_at_CET']
def generate_partial_dataset(filedir, filename):
    # Read, slice data
    raw = pd.read_csv(os.path.join(filedir, filename), engine='python', encoding='latin_1')
    
    cols = ['user_screen_name', 'latitude', 'longitude', 'text', 'created_at_CET'] # index as "doc_no", i.e. tweet id
    partial = raw[raw.lang == 'en'] # 420330 entries
    partial = partial[cols] 

    # Set original index as tweet id 
    partial['doc_no'] = partial.index 
    
    # Text cleaning
    clean_partial = clean(partial)

    # Find weather terms mentioned in each doc and save as a list
    weather_terms = pd.read_csv(os.path.join(filedir, "weather_terms.csv")).terms.tolist()
    lem_data, data_no_stop = word_to_list(clean_partial)
    term_col = [[word for word in line if word in weather_terms] for line in data_no_stop]
    clean_partial['terms'] = term_col

    # save to csv
    clean_partial.to_csv(os.path.join(filedir, "partial_clean_term.csv"), index=False)



# Create topic json files
def generate_type_topics(filedir):
    raw = pd.read_csv(os.path.join(filedir, "partial_clean_term.csv"), engine='c', encoding='latin_1')

    event_mild = pd.read_csv(os.path.join(filedir, 'new_mild.csv'))
    event_severe = pd.read_csv(os.path.join(filedir, 'new_severe.csv'))   
    event_df = pd.concat([event_mild, event_severe]).reset_index(drop=True)
    
    for i in range(event_df.shape[0]):
        ttpye = event_df.event[i]       
        doc_list = literal_eval(event_df.loc[i, 'doc_list'])     
        docs = raw[raw.doc_no.isin(doc_list)]
        lem, dlist = word_to_list(docs)

        num_topics = 4
        num_words = 10
        ldamodel = gensim_lda(lem,n_topic=num_topics,n_word=num_words)
        topic_list = []
        for t in range(num_topics):
            t_dict = {}
            t_dict["topic"] = t
            t_dict["pairs"] = ldamodel.show_topic(t)
            topic_list.append(t_dict)
        if ttpye == 'dusk/dawn':
            ttpye = 'dusk_dawn'
        if not os.path.isdir(filedir+'/termtopic'):
            os.mkdir(filedir+'/termtopic')
        save_topic(topic_list,filedir+'/termtopic/'+ttpye+'.json')


def main():
    generate_partial_dataset(FILE_DIR, DATAFILE)
    generate_type_topics(FILE_DIR)


if __name__ == '__main__':
    main()

