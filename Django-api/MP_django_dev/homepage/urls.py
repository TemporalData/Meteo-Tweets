from django.urls import path

from . import views

urlpatterns = [

    path("", views.homepage, name="homepage"),
    path("login/", views.login, name="login"),
    path("timeline/", views.timeline, name="timeline"),
    path("leaflet/", views.leaflet, name="leaflet"),
    path("d3map/", views.d3map, name="d3 map testing"),
    path("test/", views.testing, name="testing"),

]
