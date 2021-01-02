from django.contrib import admin

# Register your models here.

from .models import Document, WeatherTerm 

admin.site.register(Document)
admin.site.register(WeatherTerm)