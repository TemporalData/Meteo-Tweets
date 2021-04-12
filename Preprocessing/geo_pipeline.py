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
    pbar = tqdm(total=7)

    # Read, slice data
    cleaned = pd.read_csv(
        os.path.join(filedir, filename),
        engine='python',
        encoding='latin_1')

    pbar.update(1)

    # Columns that the geo model requires
    cols = ['latitude', 'longitude']

    partial = cleaned.loc[:, cols]
    pbar.update(1)

    # Set original index as tweet id
    partial['ID'] = partial.index
    pbar.update(1)

    partial = partial.loc[:, ['ID']+cols]
    pbar.update(1)

    partial.loc[:, 'latitude'] = round(round(partial['latitude']/5, 3)*5, 4)
    pbar.update(1)
    partial.loc[:, 'longitude'] = round(round(partial['longitude']/5, 3)*5, 4)
    pbar.update(1)

    f = open(os.path.join(filedir, "geo_model.csv"), "w")
    np.savetxt(f, partial, fmt=','.join(['%i'] + ['%1.4f']*2))
    f.close()
    pbar.update(1)

    pbar.close()


def main():
    generate_geo_data(FILE_DIR, DATAFILE)


if __name__ == '__main__':
    main()
