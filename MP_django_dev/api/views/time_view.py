from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import HttpResponse

# Import the model from the app timeline
from timeline.models import TimeData
# Import function from processing.py from the app timelineW
from timeline.processing import compute_timeline

# Import numpy
import numpy as np
import pandas as pd
from datetime import datetime


###
# APIView for the temporal filtering of tweet ids
# Input:
# id_filter - list of ids which will be used for the filtering
#             empty means use all ids present
# start     - date which represents the start of the filter
# end       - date which represents the end of the filter
#
# Output:
# list of ids where all tweets happened between the passed start and end dates
# If id_filter is nonempty the output is always a subset of the id_filter list,
# that includes the possiblity all of the ids in id_filter being in the output
###
class TimeFilterAPI(APIView):

    # Rest framework classes for authentication
    authentication_classes = []
    permission_classes = []

    # Define the response of a 'GET' request
    def get(self, request):

        # Retrieve the parsed parameters from the request
        try:
            # Load the list in the request into id_filter variable
            id_filter = request.query_params['id_filter']
            # Load the other required variables from the request
            start = request.query_params['start']
            end = request.query_params['end']

        # Catch exceptions caused by missing parameters
        except Exception:
            # Return a bad request status due to
            # lacking either 'id_filter', 'start', or 'end'
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Check whether start and end variables are the right format
        try:
            # Attempt to convert the variables into datetime
            start_datetime = datetime.strptime(start, "%d/%m/%Y")
            end_datetime = datetime.strptime(end, "%d/%m/%Y")

        # If the format is incorrect an exception will be thrown
        except Exception:
            # Return bad request as start or end is in the wrong format
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Try to retrieve the data from the TimeData model
        try:
            # If id_filter is not empty
            if len(id_filter) > 0:
                # Transform id_filter into an int list
                id_filter = list(map(int, id_filter.split(',')))
                # Load the filtered data into the 'data' variable
                data = TimeData.objects.values_list("id", flat=True).filter(
                    id__in=id_filter).filter(
                    time_created__range=(start_datetime, end_datetime)
                    )
            # 'id_filter' is empty list
            else:
                # Set 'data' to all the entries in the Data model
                data = TimeData.objects.values_list("id", flat=True).filter(
                    time_created__range=(start_datetime, end_datetime)
                    )
        # If the TimeData model does not exist
        except TimeData.DoesNotExist:
            # Return a internal server error, as TimeData model isn't populated
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return the id's filtered by time
        return Response(data)


###
# APIView for retrieving the timeline data
# Input:
# id_filter - list of ids which will be used for the filtering
#             empty means use all ids present
#
# Output:
# 2D array with each row being the date and the amount of tweets on that day
###
class TimeLineDataAPI(APIView):

    # Rest framework classes for authentication
    authentication_classes = []
    permission_classes = []

    # Define the response of a 'GET' request
    def get(self, request):

        # Retrieve the id_filter from the request
        try:
            # Load the list in the request into id_filter variable
            id_filter = request.query_params['id_filter']

        # Catch exceptions caused by 'id_filter' not being in the request
        except Exception:
            # Return a bad request status due to lacking 'id_filter
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Try to retrieve the data from the TimeData model
        try:
            # If id_filter is not empty
            if len(id_filter) > 0:
                # Transform id_filter into an int list
                id_filter = list(map(int, id_filter.split(',')))
                # Load the filtered data into the 'data' variable
                data = TimeData.objects.filter(
                    id__in=id_filter).values_list('time_created', flat=True)

            # 'id_filter' is empty list
            else:
                # Set 'data' to all the entries in the TimeData model
                data = TimeData.objects.values_list('time_created', flat=True)

        # If the TimeData model does not exist
        except TimeData.DoesNotExist:
            # Return a internal server error, as TimeData model isn't populated
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        output = pd.DataFrame(compute_timeline(data), dtype='str')

        output.columns = ['pub_date', 'count']

        output['count'] = pd.to_numeric(output['count'])

        # Formatting for the output
        json_output = output.to_json(orient="records")

        # Return the desired data from the output of compute_timeline
        # This is found in file 'processing.py' in the timeline app

        return HttpResponse(json_output, content_type="application/json") 
        # Response(compute_timeline(data))
