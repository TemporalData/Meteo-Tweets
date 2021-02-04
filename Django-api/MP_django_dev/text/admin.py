from django.contrib import admin

# Register your models here.

from .models import Document, WeatherTerm, TermType

admin.site.register(Document)
admin.site.register(WeatherTerm)