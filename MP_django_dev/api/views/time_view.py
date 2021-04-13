from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# Import the model from the app timeline
from timeline.models import TimeData
# Import function from processing.py from the app timelineW
from timeline.processing import compute_timeline

# Import numpy
import numpy as np
import pandas as pd
from datetime import datetime


###
# Takes ID list and returns:
# Latitude, longitude, density
###


class TimeDataAPI(APIView):

    # Rest framework classes for authentication
    authentication_classes = []
    permission_classes = []

    # Define the response of a 'GET' request
    def get(self, request):

        # Retrieve the id_filter from the request
        try:
            # Load the list in the request into id_filter variable
            id_filter = request.query_params['id_filter']
            start = request.query_params['start']
            end = request.query_params['end']

        # Catch exceptions caused by 'id_filter' not being in the request
        # Or the varialbes start or end
        except Exception:
            # Return a bad request status due to lacking 'id_filter
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

        # Try to retrieve the data from the Data model
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
        # If the Data model does not exist
        except TimeData.DoesNotExist:
            # Return a internal server error, as Data model isn't populated
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return the id's filtered by time
        return Response(data)


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

        # Try to retrieve the data from the Data model
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
                # Set 'data' to all the entries in the Data model
                data = TimeData.objects.values_list('time_created', flat=True)
        # If the Data model does not exist
        except TimeData.DoesNotExist:
            # Return a internal server error, as Data model isn't populated
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = np.fromiter(data, np.dtype('datetime64[D]'))

        data = data.astype('str')

        timeline_data = compute_timeline(data)

        # Return the map data
        return Response(timeline_data)
