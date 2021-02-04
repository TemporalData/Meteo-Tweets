from django.shortcuts import render

# Create your views here.


def homepage(request):

    return render(request, "homepage.html")


def login(request):

    return render(request, "loginpage.html")
  
def timeline(request):

    return render(request, "test.html")
  
def d3map(request):

    return render(request, "d3map.html")


def testing(request):

    return render(request, "test2.html")


def leaflet(request):

    return render(request, "leaflet-test.html")
