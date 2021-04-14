import numpy as np
from datetime import datetime
from numba import njit


# Function adds 0 frequency dates so the visualization is correct
# Input 2D Array with [dates, frequencies of tweets]
# Output: 2D Array with [dates, frequencies of tweets]
def pad_date_freq(array_df):

    # Declare empty lists for the new dates and frequencies
    new_dates = [array_df[0][0]-1]
    new_freq = [0]

    # Declare a counter to keep track of the date been looked at
    current_date = array_df[0][0]

    # Loop the parsed frequency array
    # Pad dates where the interval is larger than 1 day
    for i in range(0, len(array_df[0])-1):

        # Add the current date to the new_dates list
        new_dates.append(array_df[0][i])
        # Add the corresponding frequency as well
        new_freq.append(array_df[1][i])

        # Compute the day following this entry
        next_date = (array_df[0][i]+1)
        # Check whether the following entry is also the following day
        if(next_date != array_df[0][i+1]):

            # Add the following date to the list with freq 0
            new_dates.append(next_date)
            new_freq.append(0)

            # Check if the next entry is more than 2 days from this one
            if(next_date != array_df[0][i+1]-1):

                # Add the day before the next entry to the list with freq 0
                new_dates.append(array_df[0][i+1]-1)
                new_freq.append(0)

    # As the comparisons in the for above were forward looking
    # Add the last entry and its frequency
    new_dates.append(array_df[0][-1])
    new_freq.append(array_df[1][-1])

    # Add a day at the end which is after the last entry with freq 0
    new_dates.append(array_df[0][-1]+1)
    new_freq.append(0)

    return([new_dates, new_freq])


def compute_timeline(timeline_queryset):

    # Reformat the datetime to days
    timeline_data = np.fromiter(timeline_queryset, np.dtype('datetime64[D]'))

    # Find the unique days and their corresponding frequencies
    timeline_data = np.unique(timeline_data, return_counts=True)

    # Return the padded array
    return (pad_date_freq(timeline_data))
