from rest_framework import serializers
from .models import Trend, Tweet, Topic, Location,GeoPlaces
from .models import User



class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = ['url','id','text','id','like_count','retweet_count',
        'reply_count','source','user_id','user_name','user_followers','trend','is_calculated']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['url','id','location']
        
class GeoPlacesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeoPlaces
        fields = ['url','id','place']


class TrendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trend
        fields = ['url','id','name', 'volume','locations','as_of','created','is_active','is_user_trend','users']
        read_only_fields = ('volume',)


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['url','id','name','trend',]
