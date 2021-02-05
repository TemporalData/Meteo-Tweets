from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.db import connections
from django.db.models import Count
from django.http import JsonResponse
from django.core import serializers
# from django.contrib.postgres.aggregates.general import ArrayAgg
import json
from text.models import Document, WeatherTerm, TermType

import random
import os
import re
import numpy as np
import pandas as pd
from ast import literal_eval

from text import topic_pipeline as tp
# from . import text_processing as process
from network import generate_network as gn

from django.utils import timezone
today = timezone.now()

CURRENT_PATH = os.getcwd()+'/static/data/'
DATA_PATH = CURRENT_PATH + 'partial.csv'
DOCFILE = "test.csv"#"partial_clean_term.csv"#"test.csv" Or "partial_clean_term.csv" after done with test(load takes a long time)


def dashboard(request):
    
    
# Update timeline with termtype-related data
    if(request.GET.get('termtype')):
        data = {'response': count_tweet(request.GET.get('termtype'))}
        return JsonResponse(data)   

# Part 1: update wordcloud
    # Acquire new start and end dates, and apply clustering algorithm
    elif(request.GET.get('apply_change')):
        start = request.GET.get('start')
        end = request.GET.get('end')   
        response_data = fetch_date(start,end,CURRENT_PATH) 
        data = {'response': [f'start date is: {start}, end date is {end}', response_data]} 
        return JsonResponse(data)

# Part 2: update weather event's topics
    elif(request.GET.get('selected_event')):
        start = request.GET.get('start')
        end = request.GET.get('end')  
        selections = [item for item in request.GET.get('selected_event').split(',')] 
        raw_text, flat_js= topic_extract(start,end,selections)

        data = {'response': f'selected_event is {selections}', 'text':raw_text,'topics':flat_js,} 
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
    
# Load the default webpage 
    else:
        # Overwrite database (Approximate 15 mins for creating a complete database!!!) 

        # _clear_db()
        # _create_db('T')  # Create termtype objects
        # _create_db('DW') # Create document and weather term objects 


        # events = pd.read_csv(CURRENT_PATH+'new_weather.csv').iloc[:,0].values.tolist()
        mild = pd.read_csv(CURRENT_PATH+'new_mild.csv')
        severe = pd.read_csv(CURRENT_PATH+'new_severe.csv')

        merged_mild = mild.loc[:,['event','keywords']].to_dict('records')
        merged_severe = severe.loc[:,['event','keywords']].to_dict('records')
        merged_groups = merged_mild + merged_severe
        event_mild = mild.iloc[:,0].values.tolist()
        event_severe = severe.iloc[:,0].values.tolist()
        event_groups = [{"key":"Mild Weather Events","value":event_mild},{"key":"Severe Weather Events","value":event_severe}]
      
        context = {'place':'No date selected!', "event_groups":json.dumps(event_groups), "merged_terms": json.dumps(merged_groups)}

        return render(request, 'dashboard.html', context=context)        



def count_tweet(input):
    if input == "all":
        result = Document.objects.values('pub_date').annotate(count=Count('pub_date')).order_by('pub_date')
    else:
        result = Document.objects.values('pub_date','terms__ttype__typename').filter(terms__ttype__typename=input).annotate(count=Count('pub_date')).order_by('pub_date')
    
    return list(result)


def topic_extract(start,end, event):
    
    selected_text = Document.objects.filter(pub_date__gte=start, pub_date__lte=end).filter(terms__isnull=False).filter(terms__ttype__typename__in=event).distinct().values_list('text',flat=True)
    response_data = json.dumps(list(selected_text))

    # perform LDA on selected_text
    if tp.lda_process(list(selected_text)):
        topicsJ = json.dumps(tp.lda_process(list(selected_text)))
        return response_data,topicsJ
    return response_data, False





def fetch_date(start,end,filepath):
    selected_docs = Document.objects.values('doc_idx','terms__term').filter(terms__isnull=False).filter(pub_date__gte=start, pub_date__lte=end)
    response_data = json.dumps(list(selected_docs)) # [{'term1':1}, {'term2':2}]

    return response_data


# def _load_csv(filedir,start,end):
def _create_db(model):

    # Create TermType objects
    if model == 'T':
        milddir = CURRENT_PATH + 'new_mild.csv'
        mild = pd.read_csv(milddir, engine='python')

        severedir = CURRENT_PATH + 'new_severe.csv'
        severe = pd.read_csv(severedir, engine='python')

        for line in mild.iterrows():
            new_type = TermType.objects.create(
                typename = line[1]['event'],)
            # Add new ttype to matching weatherterm objects
            for term in line[1]['keywords'].split(','):
                try:
                    match_term = WeatherTerm.objects.get(term=term)
                except WeatherTerm.DoesNotExist:
                    match_term = WeatherTerm.objects.create(term=term)
                match_term.ttype = new_type
                match_term.save()

        for line in severe.iterrows():
            new_type = TermType.objects.create(
                typename = line[1]['event'])
            # Add new ttype to matching weatherterm objects
            for term in line[1]['keywords'].split(','):
                try:
                    match_term = WeatherTerm.objects.get(term=term)
                except WeatherTerm.DoesNotExist:
                    match_term = WeatherTerm.objects.create(term=term)
                match_term.ttype = new_type
                match_term.save()

            
    # Create Document and WeatherTerm objects
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
    try:
        Document.objects.all().delete()
    except Document.DoesNotExist:
        pass
    try:
        WeatherTerm.objects.all().delete()
    except WeatherTerm.DoesNotExist:
        pass
    try:
        TermType.objects.all().delete()
    except TermType.DoesNotExist:
        pass


    return '_clear_db is done!'













