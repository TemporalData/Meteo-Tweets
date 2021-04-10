#!/bin/bash
# $bash clear.sh
python manage.py makemigrations
python manage.py migrate --run-syncdb
python manage.py migrate
python manage.py runserver