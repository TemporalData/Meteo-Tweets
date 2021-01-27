from rest_framework import serializers

from geo_map.models import GeoData, GeoCache


class GeoDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = GeoData
        fields = ['latitude', 'longitude']


class GeoCacheSerializer(serializers.ModelSerializer):

    data_list = serializers.ListField(child=serializers.FloatField())

    class Meta:
        model = GeoCache
        fields = '__all__'
