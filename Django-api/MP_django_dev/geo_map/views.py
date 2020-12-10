from django.shortcuts import render

import requests
import numpy as np

from .timeline_plot import render_timeline


def index(request):

    r = requests.get(
        'http://127.0.0.1:8000/api/timeline/',
        params={"id_filter": ""})

    data = r.text.strip('[]').split("],[")

    script, div = render_timeline(
        data[0].split(','),
        list(map(int, data[1].split(','))))

    # Feed them to the Django template.
    return render(request, 'bokeh.html', context={
        'script': script, 'div': div})
