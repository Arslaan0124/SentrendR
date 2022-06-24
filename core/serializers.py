from rest_framework import serializers
from .models import Trend, Tweet, Topic, Location,GeoPlaces,TrendSentiment,TrendStats,TrendSources
from .models import User



class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = ['url','id','text','id','like_count','retweet_count',
        'reply_count','source','user_id','user_name','user_followers','trend']

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

class TrendStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrendStats
        fields = ['url','id','like_count','reply_count','retweet_count','min_followers','max_followers','average_followers','calculated_upto','trend_sources']

class TrendSourcesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrendSources
        fields = ['url','id','source_name','trend_stats']

class TrendSentimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrendSentiment
        fields = ['url','id','pos_pol_count','neg_pol_count',"neu_pol_count",'sub_count','obj_count','calculated_upto','top_pos_1','top_pos_2','top_pos_3','top_neg_1','top_neg_2','top_neg_3','top_neu_1','top_neu_2','top_neu_3']