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
    cols = ['tweet_id', 'latitude', 'longitude']

    export = cleaned.loc[:, cols]
    pbar.update(1)

    export.loc[:, 'latitude'] = round(round(export['latitude']/5, 3)*5, 4)
    pbar.update(1)
    export.loc[:, 'longitude'] = round(round(export['longitude']/5, 3)*5, 4)
    pbar.update(1)

    # counter for the index of the locations
    counter_index = 1
    # Variable to store the current location
    current_lat_long = np.array(export.loc[0, ['latitude', 'longitude']])
    # List to store location index of each tweet
    location_pointer_list = [1]
    # List to store the locations
    location_list = [current_lat_long]

    pbar.update(1)

    loopbar = tqdm(total=(len(export)-1))

    for i in range(1, len(export)):
        selected_lat_long = np.array(export.loc[i, ['latitude', 'longitude']])

        if((selected_lat_long == current_lat_long).all()):
            location_pointer_list.append(counter_index)
        else:
            location_list.append(selected_lat_long)
            counter_index += 1
            location_pointer_list.append(counter_index)
            current_lat_long = selected_lat_long
        loopbar.update(1)

    pbar.update(12)

    # Creating the object which holds all columns for the GeoLocation Model
    export_GeoLocation = pd.DataFrame(location_list)
    export_GeoLocation.columns = ['latitude', 'longitude']
    export_GeoLocation['id'] = np.arange(1, len(export_GeoLocation)+1)
    export_GeoLocation = export_GeoLocation.loc[
        :, ['id', 'latitude', 'longitude']]

    pbar.update(5)

    export['geo_location_id'] = location_pointer_list

    # Selecting the columns relevant for the GeoTweet model
    export_GeoTweet = export.loc[:, ['tweet_id', 'geo_location_id']]
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
