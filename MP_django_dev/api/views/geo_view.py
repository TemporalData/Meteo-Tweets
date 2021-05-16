from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import HttpResponse

# Import the model from the app geo map
from geo_map.models import GeoLocation, GeoTweet
# Import function from processing.py from the app geo map
from geo_map.processing import density_to_color, compute_geo_location_density
# Import the model for time filtering
from timeline.models import TimeData

# Import numpy
import numpy as np
import pandas as pd
from datetime import datetime


class GeoFilterAPI(APIView):

    # Rest framework classes for authentication
    authentication_classes = []
    permission_classes = []

    # Define the response of a 'GET' request
    def get(self, request):

        # Retrieve the geo_id_filter from the request
        try:
            # Load request parameters into their variables
            id_filter = request.query_params['id_filter']
            geo_id_filter = request.query_params['geo_id_filter']

        # Catch exceptions caused by either 'id_filter' or 'geo_id_filter'
        # not being in the request
        except Exception:
            # Return a bad request status
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Try to retrieve the data from the GeoTweet model
        try:
            # Filter only on tweet id's
            if len(id_filter) > 0 and len(geo_id_filter) == 0:
                # Transform id_filter into an int list
                id_filter = list(map(int, id_filter.split(',')))

                # Load the filtered data into the 'data' variable
                data = GeoTweet.objects.filter(
                    id__in=id_filter
                    ).values_list('id', flat=True)

            # Filter only on geo location id's
            elif len(id_filter) == 0 and len(geo_id_filter):
                # Transform geo_id_filter into an int list
                geo_id_filter = list(map(int, geo_id_filter.split(',')))

                # Load the filtered data into the 'data' variable
                data = GeoTweet.objects.filter(
                    geo_location_id__in=geo_id_filter
                    ).values_list('id', flat=True)

            # Filter on both tweet id's and geo location id's
            elif len(id_filter) > 0 and len(geo_id_filter) > 0:
                # Transform filters into an int list
                id_filter = list(map(int, id_filter.split(',')))
                geo_id_filter = list(map(int, geo_id_filter.split(',')))

                # Load the filtered data into the 'data' variable
                data = GeoTweet.objects.filter(
                    geo_location_id__in=geo_id_filter
                    ).filter(
                    id__in=id_filter
                    ).values_list(
                        'id', flat=True)
                pass

            # Filters are empty, hence return all
            else:
                data = GeoTweet.objects.all().values_list('id', flat=True)

        # If the Data model does not exist
        except GeoTweet.DoesNotExist:
            # Return a internal server error, as Data model isn't populated
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # # Return the id's filtered by time
        return Response(data)


class GeoDataAPI(APIView):

    # Rest framework classes for authentication
    authentication_classes = []
    permission_classes = []

    # Define the response of a 'GET' request
    def get(self, request):

        # Retrieve the id_filter from the request
        try:
            # Load the other required variables from the request
            start = request.query_params['start']
            end = request.query_params['end']

        # Catch exceptions caused by missing parameters
        except Exception:
            # Return a bad request status due to
            # lacking either 'id_filter', 'start', or 'end'
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if(len(start) > 0 or len(end) > 0):
            # Check whether start and end variables are the right format
            try:
                # Attempt to convert the variables into datetime
                start_datetime = datetime.strptime(start, "%d-%m-%Y")
                end_datetime = datetime.strptime(end, "%d-%m-%Y")

            # If the format is incorrect an exception will be thrown
            except Exception:
                # Return bad request as start or end is in the wrong format
                return Response(status=status.HTTP_400_BAD_REQUEST)

            try:
                time_ids = TimeData.objects.values_list(
                    "id", flat=True).filter(
                    time_created__range=(start_datetime, end_datetime))

            # If the TimeData model does not exist
            except TimeData.DoesNotExist:
                # Return a internal server error, as model isn't populated
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            try:
                # Load the filtered data into the 'data' variable
                data = GeoTweet.objects.filter(
                    id__in=time_ids).values_list(
                        'geo_location', flat=True)
            # If the GeoTweet model does not exist
            except GeoTweet.DoesNotExist:
                # Return a internal server error, as Data model isn't populated
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            try:
                data = GeoTweet.objects.all().values_list(
                    'geo_location', flat=True)
            # If the GeoTweet model does not exist
            except GeoTweet.DoesNotExist:
                # Return a internal server error, as Data model isn't populated
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        geo_ids, densities = compute_geo_location_density(data)

        # Try to retrieve data from the GeoLocation model
        try:

            locations = GeoLocation.objects.filter(
                    id__in=geo_ids).values_list(
                        'id',
                        'latitude',
                        'longitude')

        # If the model does not exist
        except GeoLocation.DoesNotExist:
            # Return a internal server error,
            # as GeoLocation model isn't populated
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Format the data for the output
        output = pd.DataFrame.from_records(locations)

        # Add columns for the output
        output.columns = ["id", "lat", "long"]

        # Calculate the densities at each point
        density_colors = density_to_color(densities)

        # Add these densities to the dataframe
        output["color"] = density_colors

        # Formatting for the output
        json_output = output.to_json(orient="records")

        # Return the map data
        return HttpResponse(json_output, content_type="application/json")
