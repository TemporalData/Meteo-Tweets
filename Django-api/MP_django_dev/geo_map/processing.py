import numpy as np
import pandas as pd
import math

# Function to compute the map points and their densities given one array
# Input = [ latitude values, longitude values]
# Output = {" latitude"  = [...] , " latitude"  = [...], "density" = [...]}
# Where for each unique lat and longitude there is a corresponding density


def compute_map_data(latLongData):

    return compute_map_densities(latLongData)


def compute_map_densities(latLongData):

    # Give the inputted dataframe column names for clarity
    latLongData.columns = ['latitude', 'longitude']

    # Sort the list based on latitude and longitude
    latLongData = latLongData.sort_values(by=['latitude', 'longitude']).copy()

    # Reset the index for the calculation of densities
    latLongData = latLongData.set_index(np.arange(0, len(latLongData)))

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

    # Add the column to the latLongData
    latLongData['density'] = density

    return latLongData


def density_to_color(density_array):

    # Store the maximal density
    max = density_array.max()

    # Declare an empty list to contain the colors
    color_list = []

    # Loop all the densities and compute the colors
    for density in density_array:
        color = density_color_map(density, max)
        color_list.append(color)
    return (np.array(color_list))


def density_color_map(value, max):
    palette = [
        '#000e5c', '#000f5e', '#000f60', '#011061', '#011063', '#011165',
        '#021166', '#031268', '#031269', '#04126b', '#05136c', '#07136e',
        '#081470', '#091471', '#0b1473', '#0d1574', '#0e1576', '#101677',
        '#121678', '#13167a', '#15177b', '#17177d', '#19177e', '#1b187f',
        '#1d1880', '#1f1882', '#211883', '#231984', '#251985', '#271986',
        '#291988', '#2b1a89', '#2d1a8a', '#2f1a8b', '#311a8c', '#341a8c',
        '#361a8d', '#391a8e', '#3b1a8f', '#3d1a8f', '#401a90', '#431a90',
        '#451a91', '#481a91', '#4b1991', '#4e1992', '#501992', '#531892',
        '#561892', '#591792', '#5b1792', '#5e1692', '#601692', '#631692',
        '#651592', '#681592', '#6a1492', '#6d1491', '#6f1391', '#711391',
        '#741291', '#761291', '#781191', '#7a1191', '#7c1090', '#7f1090',
        '#810f90', '#830f90', '#850e90', '#870e8f', '#890d8f', '#8b0d8f',
        '#8d0c8e', '#8f0c8e', '#910c8e', '#930b8d', '#950b8d', '#970b8d',
        '#990a8c', '#9b0a8c', '#9d0a8c', '#9f098b', '#a1098b', '#a3098a',
        '#a5098a', '#a7098a', '#a90989', '#aa0989', '#ac0988', '#ae0988',
        '#b00988', '#b20987', '#b30a87', '#b50a86', '#b70a86', '#b90b85',
        '#ba0b85', '#bc0c85', '#be0c84', '#bf0d84', '#c10d83', '#c30e83',
        '#c40e82', '#c60f82', '#c81081', '#c91181', '#cb1180', '#cd1280',
        '#ce137f', '#d0147f', '#d1167e', '#d3177e', '#d4187d', '#d61a7c',
        '#d71b7c', '#d81d7b', '#da1e7a', '#db2079', '#dc2179', '#de2378',
        '#df2577', '#e02676', '#e12876', '#e22a75', '#e32c74', '#e42d73',
        '#e62f72', '#e73171', '#e83370', '#e9356f', '#e9366e', '#ea386d',
        '#eb3a6c', '#ec3c6b', '#ed3e6a', '#ee4069', '#ee4267', '#ef4466',
        '#f04565', '#f14764', '#f14963', '#f24b62', '#f24d61', '#f34f60',
        '#f3515f', '#f4525e', '#f4545d', '#f5565c', '#f5585b', '#f65a5a',
        '#f65c59', '#f65e58', '#f75f57', '#f76157', '#f76356', '#f86555',
        '#f86754', '#f86953', '#f86a52', '#f86c52', '#f86e51', '#f87050',
        '#f87250', '#f8744f', '#f8754e', '#f8774e', '#f8794d', '#f87b4c',
        '#f87d4c', '#f87e4b', '#f8804a', '#f8824a', '#f88349', '#f88548',
        '#f88748', '#f88847', '#f88a47', '#f88c46', '#f88d45', '#f98f45',
        '#f99044', '#f99243', '#f99343', '#f99542', '#f99641', '#f99841',
        '#f99940', '#f99b3f', '#f99c3f', '#fa9e3e', '#fa9f3d', '#faa03d',
        '#faa23c', '#faa33b', '#faa53b', '#fba63a', '#fba73a', '#fba939',
        '#fbaa39', '#fbab38', '#fbad38', '#fcae38', '#fcb037', '#fcb137',
        '#fcb237', '#fcb437', '#fcb537', '#fcb637', '#fcb837', '#fcb937',
        '#fcbb37', '#fcbc38', '#fcbd38', '#fcbf38', '#fcc038', '#fcc238',
        '#fcc339', '#fcc439', '#fcc639', '#fcc73a', '#fcc83a', '#fcca3a',
        '#fccb3b', '#fccd3b', '#fbce3b', '#fbcf3c', '#fbd13c', '#fbd23d',
        '#fbd33d', '#fbd53e', '#fbd63e', '#fbd83f', '#fad93f', '#fada40',
        '#fadc40', '#fadd41', '#fade41', '#f9e042', '#f9e142', '#f9e243',
        '#f9e444', '#f9e544', '#f8e745', '#f8e845', '#f8e946', '#f8eb47',
        '#f7ec47', '#f7ed48', '#f7ef48', '#f7f049', '#f6f14a', '#f6f34a',
        '#f6f44b', '#f5f64c', '#f5f74d', '#f5f84d']

    color_index = round((math.log10(value)/math.log10(max))*255)

    return palette[color_index]
