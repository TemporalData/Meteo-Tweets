# Import pandas for the csv import
import pandas as pd
import numpy as np
import os

#  Dataset name and directories
FILE_DIR = os.path.join(os.getcwd(), 'data')  # Directory to save output
DATAFILE = 'cleaned_dataset.csv'  # Original dataset


def generate_geo_map(filedir, filename):
    # Read, slice data
    raw = pd.read_csv(
        os.path.join(filedir, filename),
        engine='python',
        encoding='latin_1')

    cols = ['latitude', 'longitude']  # index as "doc_no", i.e. tweet id

    partial = raw.loc[:, cols]

    # Set original index as tweet id
    partial['doc_no'] = partial.index

    print(partial.head())


def main():
    print("Generating geo map model data")
    generate_geo_map(FILE_DIR, DATAFILE)
    print("Done.")


if __name__ == '__main__':
    main()
