from django.urls import path

from .views import geo_view, time_view

app_name = 'api'

urlpatterns = [
    path("geo/", geo_view.GeoDataAPI.as_view()),
    path("time/", time_view.TimeDataAPI.as_view()),
    path("timeline/", time_view.TimeLineDataAPI.as_view()),
]
