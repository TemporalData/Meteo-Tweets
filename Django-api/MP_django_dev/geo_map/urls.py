from django.urls import path, include

from . import views

urlpatterns = [

    path("bokeh/", views.index, name="bokeh"),

    # path("<int:pk>/", views.tweet_detail, name="tweet_detail"),

]
