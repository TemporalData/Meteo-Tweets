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
    pbar = tqdm(total=4)

    # Read, slice data
    cleaned = pd.read_csv(
        os.path.join(filedir, filename),
        engine='python',
        encoding='latin_1')

    pbar.update(1)

    # Columns that the geo model requires
    cols = ['created_at_CET']

    partial = cleaned.loc[:, cols]
    pbar.update(1)

    # Set original index as tweet id
    partial['ID'] = partial.index
    partial = partial.loc[:, ['ID']+cols]
    pbar.update(1)

    # save to csv
    partial.to_csv(
        os.path.join(filedir, "timeline_model.csv"), index=False)

    pbar.update(1)

    pbar.close()


def main():
    generate_geo_data(FILE_DIR, DATAFILE)


if __name__ == '__main__':
    main()