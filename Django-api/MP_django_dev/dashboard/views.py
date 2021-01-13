from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.db import connections
from django.db.models import Count
from django.http import JsonResponse
from django.core import serializers
# from django.contrib.postgres.aggregates.general import ArrayAgg
import json
from text.models import Document, WeatherTerm

import random
import os
import re
import numpy as np
import pandas as pd
from ast import literal_eval

# from . import text_processing as process
from network import generate_network as gn

from django.utils import timezone
today = timezone.now()

CURRENT_PATH = os.getcwd()+'/static/data/'
DATA_PATH = CURRENT_PATH + 'partial.csv'
DOCFILE = "test.csv"#"partial_clean_term.csv"#"test.csv" Or "partial_clean_term.csv" after done with test(load takes a long time)


def dashboard(request):
    
    # weatherterms = WeatherTerm.objects.all()
    # documents = Document.objects.all()

    
# Reset to default
    if(request.GET.get('submitreset')):
        context = {'place':'No date selected!'}
        return render(request, 'graph/graph.html', context=context)         

# Part 1: update wordcloud
    # Acquire new start and end dates, and apply clustering algorithm
    elif(request.GET.get('apply_change')):
        start = request.GET.get('start')
        end = request.GET.get('end')   
        response_data = _run_front_process(start,end,CURRENT_PATH) 

        data = {'response': [f'start date is: {start}, end date is {end}', response_data]} 
        return JsonResponse(data)

# Part 2: update weather event's topics
    elif(request.GET.get('selected_event')):
        selection = request.GET.get('selected_event')

        flat_js= topic_extract(selection)

        # topics = json.dumps(topics)
        # for t in topics:
        #     t_id = t[0] #integer
        #     t_str = t[1] #string, e.g. (0, '0.057*"repost"')

        # with open(CURRENT_PATH+LDAFILE) as inputfile:
        #     lda = json.load(inputfile)
        # data = {'response': lda} 
        data = {'response': f'selected_event is {selection}', 'topics':flat_js,} 
        return JsonResponse(data)


# Part 3: update social networks
    elif(request.GET.get('updated_network')):
        start = request.GET.get('start')
        end = request.GET.get('end') 
        net = request.GET.get('updated_network')

        gn.generate_json(start,end,net)
        data = {'network-info':[start,end, net]}
        return JsonResponse(data)

# Test (optional)
    elif(request.GET.get('inputValue')):
        user_input = request.GET.get('inputValue')
        data = {'response': f'You typed: {user_input}'} 
        return JsonResponse(data)
    
# Default 
    else:
        # Overwrite database and reload the webpage

        # _clear_db()
        # _create_db('DW') # Create document and weather term objects 

        # events = pd.read_csv(CURRENT_PATH+'new_weather.csv').iloc[:,0].values.tolist()
        event_mild = pd.read_csv(CURRENT_PATH+'new_mild.csv').iloc[:,0].values.tolist()
        event_severe = pd.read_csv(CURRENT_PATH+'new_severe.csv').iloc[:,0].values.tolist()
        event_groups = [{"key":"Mild Weather Events","value":event_mild},{"key":"Severe Weather Events","value":event_severe}]
        context = {'place':'No date selected!', "event_groups":json.dumps(event_groups)}

        return render(request, 'dashboard.html', context=context)        

def topic_extract(event):
    if event == 'dusk/dawn':
        event = 'dusk_dawn' # rename and direct to the topic file 
    with open(CURRENT_PATH+'termtopic/'+event+'.json','r') as event_file:
        tw_js = json.load(event_file)


    return tw_js



def fetch_date(start,end,filepath):
    selected_docs = Document.objects.values('doc_idx','terms__term').filter(terms__isnull=False).filter(pub_date__gte=start, pub_date__lte=end)
    # doc_term_list = list(selected_docs.filter(terms__isnull=False).values('doc_idx','terms__term'))#.annotate(freq=Count('terms__term')))
    # selected_docs = Document.objects.values('doc_idx','terms__term').all()
    response_data = json.dumps(list(selected_docs)) # [{'term1':1}, {'term2':2}]

    return response_data




def _run_front_process(start,end,filepath):
    response_data = fetch_date(start,end,filepath)

    return response_data




# def _load_csv(filedir,start,end):
def _create_db(model):
    if model == 'DW': # 'D'
        # Read all EN data with doc_no, user_screen_name, latitude, longitude, text, date.
        filedir = CURRENT_PATH + DOCFILE 
        raw = pd.read_csv(filedir, engine='python')

        for line in raw.iterrows():
            new_doc = Document.objects.create(
                doc_idx = line[1]['doc_no'],
                user_name = line[1]['user_screen_name'],
                latitude = line[1]['latitude'],
                longitude = line[1]['longitude'],
                # text = line[1]['text'],
                pub_date = line[1]['date'],

                        )
                
            # Many-To-Many field: terms --> [term1, term2, ...]
            if (not pd.isna(line[1]['terms'])):
                for term in literal_eval(line[1]['terms']):
                    try:
                        match_term = WeatherTerm.objects.get(term=term)
                    except WeatherTerm.DoesNotExist:
                        match_term = WeatherTerm.objects.create(term=term)

                    new_doc.terms.add(match_term)          
  



# Delete all existing objects in db
def _clear_db():
    Document.objects.all().delete()
    WeatherTerm.objects.all().delete()


    return '_clear_db is done!'













