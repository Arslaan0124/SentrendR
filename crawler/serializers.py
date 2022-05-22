from rest_framework import serializers

from crawler.models import Crawler,StreamData


class CrawlerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crawler
        fields = ['url','id','user','consumer_key','consumer_secret','access_token','access_secret','bearer_token']
        read_only_fields = ('user',)


class StreamDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamData
        fields = ['url','id','crawler','query','duration','elapsed','is_running']