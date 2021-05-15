# Social Media Analytics - Master Project

This is the Master project of
- Fan Feng        18-745-414
- Kevin Steijn    19-770-429
- Yichun Xie      18-743-617

# Description

The project is centered around creating a dashboard to allow for analysis of social media data, in this case tweets from twitter.
The analysis aims to find relations between tweets and weather events.
With this in mind we've engineered certain features from the twitter data set and visualized them to represent the temporal, geographical, and semantic information present within the tweets.

# Structure of Project

    .
    ├── MP_django_dev	# Parent folder for the django application
	│   ├── MP_django_dev		# Main django application folder
	│   ├── api			# Contains code to handle requests for data on the database
	│   ├── dashboard		# Contains code for the dashboard
	│   ├── geo_map			# Contains a model for geographical information and processing of that data
	│   ├── static			# Contains necessary materials for the front end
    │   └── timeline		# Contains a model for temporal information and processing of that data
    ├── Preliminary Work	# Previous work that contributed to the project
	│   ├── Local Visualizations	# Visualizations that can be rendered locally
	│   └── Radar Data Processing	# Processing of radar data
	├── Preprocessing	# Contains code for processing raw input data
    │   └──  data			# Folder for storing raw input data and processed data
	├── .gitignore		# Exclusion rules for the repository
    └── README.md		# Description file
	
## Download and Usage

Simply Fork, Clone, or Download on GitHub

To run the code ensure that your environment has the needed libraries by using pip:

`pip install -r requirements.txt`

There are two requirement files corresponding to the libraries needed for preprocessing and running the django application

The requirement file for the preprocessing is located [here](https://github.com/TemporalData/Meteo-Tweets/tree/master/Preprocessing/requirements.txt)

The requirement file for the django application is located [here](https://github.com/TemporalData/Meteo-Tweets/tree/master/MP_django_dev/requirements.txt)

## Dependencies

Refer to the requirement files

## Bugs

Find a bug in the project? [Open a new issue on GitHub](https://github.com/TemporalData/Meteo-Tweets/issues)
