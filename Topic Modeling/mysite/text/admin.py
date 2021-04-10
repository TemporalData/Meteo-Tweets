from django.contrib import admin

# Register your models here.

from .models import Document, RegionTopic, DocWeatherEvent

admin.site.register(Document)
admin.site.register(RegionTopic)
admin.site.register(DocWeatherEvent)
