from rest_framework import serializers

from timeline.models import TimeData


class TimeDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = TimeData
        fields = ['tweet_id', 'time_created']
