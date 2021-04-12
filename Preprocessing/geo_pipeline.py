# Import pandas for the csv import
import pandas as pd
import numpy as np
import os
from tqdm import tqdm

#  Dataset name and directories
FILE_DIR = os.path.join(os.getcwd(), 'data')  # Directory to save output
DATAFILE = 'cleaned_dataset.csv'  # Original dataset


def generate_geo_data(filedir, filename):

    # Declare a progress bar
    pbar = tqdm(total=25)

    # Read, slice data
    cleaned = pd.read_csv(
        os.path.join(filedir, filename),
        engine='python',
        encoding='latin_1')

    pbar.update(1)

    # Columns that the geo model requires
    cols = ['latitude', 'longitude']

    export = cleaned.loc[:, cols]
    pbar.update(1)

    # Set original index as tweet id
    export['tweet_id'] = export.index
    pbar.update(1)

    export = export.loc[:, ['tweet_id']+cols]
    pbar.update(1)

    export.loc[:, 'latitude'] = round(round(export['latitude']/5, 3)*5, 4)
    pbar.update(1)
    export.loc[:, 'longitude'] = round(round(export['longitude']/5, 3)*5, 4)
    pbar.update(1)

    # counter for the index of the locations
    counter_index = 0
    # Variable to store the current location
    current_lat_long = np.array(export.loc[0, ['latitude', 'longitude']])
    # List to store location index of each tweet
    location_pointer_list = [0]
    # List to store the locations
    location_list = [current_lat_long]

    pbar.update(1)

    for i in range(1, len(export)):
        selected_lat_long = np.array(export.loc[i, ['latitude', 'longitude']])

        if((selected_lat_long == current_lat_long).all()):
            location_pointer_list.append(counter_index)
        else:
            location_list.append(selected_lat_long)
            counter_index += 1
            location_pointer_list.append(counter_index)
            current_lat_long = selected_lat_long

    pbar.update(10)

    export['geo_id'] = location_pointer_list

    # Creating the object which holds all columns for the GeoLocation Model
    export_GeoLocation = pd.DataFrame(location_list)
    export_GeoLocation.columns = ['latitude', 'longitude']
    export_GeoLocation['geo_id'] = np.arange(0, len(export_GeoLocation))
    export_GeoLocation = export_GeoLocation.loc[
        :, ['geo_id', 'latitude', 'longitude']]

    pbar.update(5)

    # Selecting the columns relevant for the GeoTweet model
    export_GeoTweet = export.loc[:, ['tweet_id', 'geo_id']]
    pbar.update(1)

    # Exporting the GeoLocation model
    export_GeoLocation.to_csv(
        os.path.join(filedir, "geoLocation_model.csv"), index=False)
    pbar.update(1)

    # Exporting the GeoTweet model
    export_GeoTweet.to_csv(
        os.path.join(filedir, "geoTweet_model.csv"), index=False)
    pbar.update(1)

    pbar.close()


def main():
    generate_geo_data(FILE_DIR, DATAFILE)


if __name__ == '__main__':
    main()
