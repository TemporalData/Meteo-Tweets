from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# Import the model from the app geo map
from geo_map.models import GeoData
# Import the serializer from the app geo map
from geo_map.serializers import GeoDataSerializer
# Import function from processing.py from the app geo map
from geo_map.processing import compute_map_data

# Import numpy
import numpy as np
import pandas as pd


###
# Takes ID list and returns:
# Latitude, longitude, density
###


class GeoDataAPI(APIView):

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
                data = GeoData.objects.filter(id__in=id_filter)
            # 'id_filter' is empty list
            else:
                # Set 'data' to all the entries in the Data model
                data = GeoData.objects.all()
        # If the Data model does not exist
        except GeoData.DoesNotExist:
            # Return a internal server error, as Data model isn't populated
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Store the latitude and longitude data in a variable
        latLongData = (pd.DataFrame(data.values_list())).iloc[:, [2, 3]]

        # Call compute map data with the lat and long data
        map_data = compute_map_data(latLongData)

        # Return the map data
        return Response(map_data)
