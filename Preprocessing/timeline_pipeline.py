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
    pbar = tqdm(total=6)

    # Read, slice data
    cleaned = pd.read_csv(
        os.path.join(filedir, filename),
        engine='python',
        encoding='latin_1')

    pbar.update(1)

    # Columns that the geo model requires
    cols = ['tweet_id', 'created_at_CET']

    # Take a slice of the cleaned data
    timeline_data = cleaned.loc[:, cols]
    pbar.update(1)

    # Format the column to pandas datetime
    timeline_data['datetime'] = pd.to_datetime(
        timeline_data['created_at_CET'])
    pbar.update(1)

    # Format the datetime to a new columns which removes seconds from the time
    # "+01:00" represents CET
    timeline_data.loc[:, 'time_created'] = timeline_data.loc[
        :, 'datetime'].dt.strftime("%Y-%m-%d %H:%M +01:00")
    pbar.update(1)

    # Format the datetime to a new column which only has the calendar date
    timeline_data.loc[:, 'date'] = timeline_data.loc[
        :, 'datetime'].dt.strftime("%d-%m-%Y")
    pbar.update(1)

    # Take only the desired columns for the export
    export = timeline_data.loc[:, ['tweet_id', 'time_created', 'date']]

    # save to csv
    export.to_csv(
        os.path.join(filedir, "timeline_model.csv"), index=False)

    pbar.update(1)

    pbar.close()


def main():
    generate_geo_data(FILE_DIR, DATAFILE)


if __name__ == '__main__':
    main()
