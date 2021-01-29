from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# Import the model from the app geo map
from geo_map.models import GeoCache, GeoData, GeoLocation
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
            geoloc_filter = request.query_params['geoloc_filter']
        # Catch exceptions caused by 'id_filter' not being in the request
        except Exception:
            # Return a bad request status due to lacking
            # 'id_filter' or 'geoloc_filter'
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Try to retrieve the data from the Data model
        try:
            # If id_filter is not empty
            if len(id_filter) > 0:
                # Transform id_filter into an int list
                id_filter = list(map(int, id_filter.split(',')))

                # Load the filtered data into the 'data' variable
                data = GeoData.objects.filter(id__in=id_filter).values_list(
                    'geo_location_id',
                    flat=True)
            # 'id_filter' is empty list
            else:
                data = GeoData.objects.all().values_list(
                    'geo_location_id',
                    flat=True)
            # else:
            #     # Set 'data' to all the entries in the Data model
            #     data = GeoCache.objects.all().values_list(
            #         'data_list',
            #         flat=True)

            #     data_response = pd.DataFrame(np.array(data).T)

            #     data_response.columns = ['latitude', 'longitude', 'density']

            #     return Response(data_response)

        # If the Data model does not exist
        except GeoData.DoesNotExist:
            # Return a internal server error, as Data model isn't populated
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        densities = np.unique(np.array(data), return_counts=True)

        if len(geoloc_filter) > 0:
            geo_locations, densities_index = np.intersect1d(
                densities[0],
                geoloc_filter,
                return_indices=True)[:2]

            geoloc_densities = densities[1][densities_index]
        else:
            geo_locations = densities[0]
            geoloc_densities = densities[1]

        print(geo_locations)
        print(geoloc_densities)

        # Retrieve the lat long coordinates
        try:

            latLongData = GeoLocation.objects.filter(
                id__in=geo_locations).values_list('latitude', 'longitude')

            print("Achieved")

        # If the Data model does not exist
        except GeoLocation.DoesNotExist:
            # Return a internal server error, as Data model isn't populated
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        print(np.array(latLongData))

        # Call compute colors of map data with the lat and long data
        color_map_data = compute_map_data(latLongData)

        # Add the IDs to the dataframe
        color_map_data["id"] = dfData.iloc[:, 1]

        # Return the map data
        return Response(color_map_data)
