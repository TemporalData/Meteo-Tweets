from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import HttpResponse

# Import the model from the app geo map
from geo_map.models import GeoCache, GeoLocation, GeoTweet
# Import function from processing.py from the app geo map
from geo_map.processing import compute_map_data, density_to_color

# Import numpy
import numpy as np
import pandas as pd


###
# Takes ID list and returns:
# geo_id, latitude, longitude
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
            # Return a bad request status due to lacking
            # 'id_filter' or 'geoloc_filter'
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Try to retrieve the data from the model
        try:
            # If id_filter is not empty
            if len(id_filter) > 0:
                # Transform id_filter into an int list
                id_filter = list(map(int, id_filter.split(',')))

                # Load the filtered data into the 'data' variable
                data = GeoTweet.objects.filter(
                    id__in=id_filter).values_list(
                        'geo_location', flat=True)
            # 'id_filter' is empty list
            else:
                data = GeoTweet.objects.all().values_list(
                    'geo_location', flat=True)
            # else:
            #     # Set 'data' to all the entries in the Data model
            #     data = GeoCache.objects.all().values_list(
            #         'data_list',
            #         flat=True)

            #     data_response = pd.DataFrame(np.array(data).T)

            #     data_response.columns = ['latitude', 'longitude', 'density']

            #     return Response(data_response)

        # If the Data model does not exist
        except GeoTweet.DoesNotExist:
            # Return a internal server error, as Data model isn't populated
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        geo_location_density_array = np.unique(
            np.array(data), return_counts=True)

        geo_ids = list(geo_location_density_array[0])
        densities = geo_location_density_array[1]

        # Try to retrieve data from the GeoLocation model
        try:

            locations = GeoLocation.objects.filter(
                    id__in=geo_ids).values_list(
                        'id',
                        'latitude',
                        'longitude')

        # If the model does not exist
        except GeoLocation.DoesNotExist:
            # Return a internal server error, as Data model isn't populated
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Format the data for the output
        output = pd.DataFrame(np.array(locations))

        # Add columns for the output
        output.columns = ["id", "lat", "long"]

        density_colors = density_to_color(densities)

        output["color"] = density_colors

        json_output = output.to_json(orient="records")

        # Return the map data
        return HttpResponse(json_output, content_type="application/json")
