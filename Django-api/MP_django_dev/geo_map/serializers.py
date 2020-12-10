from rest_framework import serializers

from geo_map.models import GeoData


class GeoDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = GeoData
        fields = ['latitude', 'longitude']
