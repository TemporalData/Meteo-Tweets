import numpy as np
from datetime import datetime
from numba import njit


def compute_timeline(array_dates):

    min_date = min(array_dates)
    max_date = max(array_dates)

    date_range = np.arange(min_date, max_date, dtype='datetime64[D]')

    temp1 = np.unique(array_dates, return_counts=True)

    print(temp1)

    return(1)
