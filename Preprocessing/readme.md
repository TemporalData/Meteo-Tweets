# Description

This folder contains python scripts for data cleaning and processing.

## filter_twitter_dataset.py

*Requires complete_swiss_dataset.csv to be present in ./data*

This file is run to clean the original dataset such that the next steps take less time.
It will retain all the english tweets and the columns specified in the file.
If any pipeline changes the columns that are used you can edit the respective line in this file.

*Produces: ./data/cleaned_dataset.csv*

## geo_pipeline.py

*Requires cleaned_dataset.csv to be present in ./data*

Running this file will generate csv files corresponding to the models needed for the geographical part of the application.


## network_pipeline.py

*Current version is a placeholder for pipeline for network model*

Running this file will generate csv files corresponding to the models needed for the network part of the application.


## text_pipeline.py

*Current version is a placeholder for pipeline for text model*

Running this file will generate csv files corresponding to the models needed for the text part of the application.

## weather_pipeline.py

Placeholder for future integration of weather data.
