from django.shortcuts import render

# Create your views here.


def homepage(request):

    return render(request, "homepage.html")


def login(request):

    return render(request, "loginpage.html")


def timeline(request):

    return render(request, "test.html")
