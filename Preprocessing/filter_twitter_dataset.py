# Filter the swiss tweet data set based on language and location

import pandas as pd
import numpy as np
import os
from tqdm import tqdm

#  Dataset name and directories
# Directory to read and output data
filedir = os.path.join(os.getcwd(), 'data')
# Name of original dataset
filename = 'complete_swiss_dataset.csv'

# Initializing the progress bar
pbar = tqdm(total=10)

# Read in the data from the csv file
raw = pd.read_csv(
        os.path.join(filedir, filename),
        encoding='ISO-8859-15')

pbar.update(4)

# Columns needed for the geo map model
geo_cols = ['latitude', 'longitude']

# Columns needed for the network model
network_cols = []

# Columns needed for the text model
text_cols = ['text']

# Columns needed for the timeline model
timeline_cols = ['created_at_CET']

# Aggregate the columns
columns = geo_cols + text_cols + network_cols + timeline_cols

# Finding the ids of the tweets that are written in english
english_tweets = np.where(raw['lang'] == 'en')[0]  # 420330 entries
pbar.update(1)

# Take only the require data out of the raw data
filtered = raw.loc[english_tweets, columns]
pbar.update(1)

# Reset the index to accomodate for the new length
filtered.index = np.arange(1, len(filtered)+1)
pbar.update(1)

# Set a column for tweet id's to the values of the index
filtered['tweet_id'] = filtered.index
pbar.update(1)

# Rearrange the dataframe
filtered = filtered.loc[:, ['tweet_id']+columns]
pbar.update(1)

# Save to csv
filtered.to_csv(os.path.join(filedir, "cleaned_dataset.csv"), index=False)
pbar.update(1)

# Closing the progress bar
pbar.close()
