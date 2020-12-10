import numpy as np
import pandas as pd


# Function to compute the map points and their densities given one array
# Input = [ latitude values, longitude values]
# Output = {" latitude"  = [...] , " latitude"  = [...], "density" = [...]}
# Where for each unique lat and longitude there is a corresponding density


def compute_map_data(latLongData):

    # Give the inputted dataframe column names for clarity
    latLongData.columns = ['latitude', 'longitude']

    # Drop all the duplciates
    # which keeps the first occuring entry in the dataframe
    latLongData = latLongData.drop_duplicates(
        subset=['latitude', 'longitude']).copy()

    # Declare an array the length of the coordinates without duplicates
    # Will represent the density at each coordinate
    density = np.ones(len(latLongData))

    # Loop the array with all the coordinates
    for i in range(0, len(latLongData)-1):
        density[i] = latLongData.index[i+1] - latLongData.index[i]

    # Add the column to the Map_data
    latLongData['density'] = density

    return latLongData
