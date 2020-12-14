from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.db import connections
from django.db.models import Count
from django.http import JsonResponse
from django.core import serializers
# from django.contrib.postgres.aggregates.general import ArrayAgg
import json
from .models import Document, RegionTopic, DocWeatherEvent

import random
import os
import re
import numpy as np
import pandas as pd
from ast import literal_eval

from . import text_processing as process
from . import generate_network as gn

from django.utils import timezone
today = timezone.now()

CURRENT_PATH = os.path.abspath(os.getcwd())+'/data/'
DATA_PATH = CURRENT_PATH + 'partial.csv'
DOCFILE = 'documents.csv'
CLUFILE = 'clusters.csv'
WEAFILE = 'events.csv'
LDAFILE = 'lda.json'


def graph(request):

    regiontopics = RegionTopic.objects.all()
    documents = Document.objects.all()
    docweatherevents = DocWeatherEvent.objects.all()
    # clusters = Cluster.objects.all()


# Reset to default
    if(request.GET.get('submitreset')):
        context = {'place': 'No date selected!'}
        return render(request, 'graph/graph.html', context=context)
    # Part 1: update wordcloud
    # Acquire new start and end dates, and apply clustering algorithm
    elif(request.GET.get('apply_change')):
        start = request.GET.get('start')
        end = request.GET.get('end')
        response_data = _run_front_process(start, end, CURRENT_PATH)

        data = {'response': [
            f'start date is : {start}, end date is {end}',
            response_data]}
        return JsonResponse(data)

# Part 2: update weather event's topics
    elif(request.GET.get('selected_event')):
        selection = request.GET.get('selected_event')

        nested_topics, flat_js, max_prob, min_prob = topic_extract(selection)

        # topics = json.dumps(topics)
        # for t in topics:
        #     t_id = t[0] #integer
        #     t_str = t[1] #string, e.g. (0, '0.057*"repost"')

        # with open(CURRENT_PATH+LDAFILE) as inputfile:
        #     lda = json.load(inputfile)
        # data = {'response': lda} 
        data = {'response': f'selected_event is {selection}', 'topics':flat_js, 'extrem':[min_prob,max_prob]} 
        return JsonResponse(data)


# Part 3: update social networks
    elif(request.GET.get('updated_network')):
        start = request.GET.get('start')
        end = request.GET.get('end')
        net = request.GET.get('updated_network')

        gn.generate_json(start, end, net)
        data = {'network-info': [start, end, net]}
        return JsonResponse(data)

# Test (optional)
    elif(request.GET.get('inputValue')):
        user_input = request.GET.get('inputValue')
        data = {'response': f'You typed: {user_input}'} 
        return JsonResponse(data)

# Default
    else:

        # events = pd.read_csv(CURRENT_PATH+'new_weather.csv').iloc[:,0].values.tolist()
        event_mild = pd.read_csv(CURRENT_PATH+'new_mild.csv').iloc[:,0].values.tolist()
        event_severe = pd.read_csv(CURRENT_PATH+'new_severe.csv').iloc[:,0].values.tolist()
        event_groups = [{"key":"Mild Weather Events","value":event_mild},{"key":"Severe Weather Events","value":event_severe}]
        context = {'place':'No date selected!', "event_groups":json.dumps(event_groups)}

        return render(request, 'graph/graph.html', context=context)        


def topic_extract(event):
    topic_text = process.event_pipeline(event,CURRENT_PATH)
    topic_result = process.topic_kw_pair(topic_text)
    tw_list,max_prob,min_prob = process.save_topic(topic_result,CURRENT_PATH)

    columns=['group','variable','prob','text']
    tw_js = []
    for row in tw_list:
        row_group = dict.fromkeys(columns,0)
        row_group.update(zip(row_group,row))
        tw_js.append(row_group)


    return topic_result,tw_js,max_prob,min_prob


def _run_front_process(start,end,filepath):
    _clear_db()
    _run_back_process(start,end,filepath)
    _create_db(filepath, 'D') #create Document objects
    _create_db(filepath, 'W') #create DocWeatherEvent objects

    event = [{'event': b.event, 'doc_list': [a.doc_idx for a in b.doc_idx.all()]} for b in DocWeatherEvent.objects.prefetch_related('doc_idx')]
    response_data = [json.dumps(event)] 

    return response_data




def _run_back_process(start,end,filepath):
    process.pipeline(start,end,filepath)
    # process.find_cloud_doc(start,end,filepath)




# def _load_csv(filedir,start,end):
def _create_db(filepath,model):

    if model == 'D':
        filedir = CURRENT_PATH + DOCFILE
        raw = pd.read_csv(filedir, engine='python')

        for line in raw.iterrows():
            if RegionTopic.objects.filter(cluster_idx=line[1]['cluster_id']):
                match_cluster = RegionTopic.objects.get(cluster_idx=line[1]['cluster_id'])
            else:
                match_cluster = RegionTopic.objects.create(cluster_idx = line[1]['cluster_id'])

            new_doc = Document.objects.create(
                doc_idx = line[1]['doc_no'],
                user_name = line[1]['user_screen_name'],
                latitude = line[1]['latitude'],
                longitude = line[1]['longitude'],
                text = line[1]['text'],
                pub_date = line[1]['date'],
                cluster_idx = match_cluster
                        )
            

    if model == 'W':
        filedir = CURRENT_PATH + WEAFILE
        raw = pd.read_csv(filedir, engine='python')

        for line in raw.iterrows():
            if literal_eval(line[1]['doc_list']) != []:
                new_term = DocWeatherEvent.objects.create(
                    event = line[1]['terms'])

                # Many-To-Many field
                for index in literal_eval(line[1]['doc_list']):
                    try:
                        match_doc = Document.objects.get(doc_idx=index)
                        new_term.doc_idx.add(match_doc)
                    except Document.DoesNotExist:
                        pass


    if model == 'C':
        filedir = CURRENT_PATH + CLUFILE
        



# Delete all existing objects in db
def _clear_db():
    RegionTopic.objects.all().delete() 
    Document.objects.all().delete()
    DocWeatherEvent.objects.all().delete()
    # if RegionTopic.objects.all():
    #     RegionTopic.objects.all().delete() 
    # if Document.objects.all():
    #     Document.objects.all().delete()
    # # if Cluster.objects.all():
    # #     Cluster.objects.all().delete()
    # if DocWeatherEvent.objects.all():
    #     DocWeatherEvent.objects.all().delete()

    return '_clear_db is done!'













