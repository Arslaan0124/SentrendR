from collections import UserString
from itertools import count
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes,throttle_classes
from rest_framework.throttling import UserRateThrottle


from .models import Topic, Trend, Tweet ,Location,GeoPlaces,TrendSentiment,TrendStats,TrendSources
from. models import User
from .serializers import TweetSerializer,TrendSerializer, TopicSerializer, LocationSerializer,GeoPlacesSerializer,TrendSentimentSerializer,TrendStatsSerializer,TrendSourcesSerializer
from rest_framework.permissions import IsAuthenticated , IsAdminUser
from .import permissions


from django.db import transaction
import concurrent.futures
import datetime
from django.utils import timezone
from .constants import LOCATIONS


from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .Analysis import sentiment
from .Analysis import metrics
from .Analysis import rankings
from .Analysis.topic_modelling import TopicModelling
from django.core.cache import cache
from django.core.cache import caches
from django.urls import reverse
from django.http import HttpRequest
from django.utils.cache import get_cache_key


from crawler.views import CrawlerViewSet

# Create your views here.

'''STREAM HANDLING'''

def stream_tweet_response(tweets,stream_data):
    keys = stream_data.query
    keys = keys.split(',')
    td = {}
    for key in keys:
        td[key] = get_trend_from_query(key)


    updated = []

    for tweet in tweets:
        # print("tweet trend",tweet['trend'])
        # print("td trend",td[tweet['trend']])
        try:
            new_tweet,created  = Tweet.objects.get_or_create(tid = tweet['id'],
                defaults = {
                    'text' : tweet['text'],
                    'like_count' :tweet['likes'],
                    'retweet_count' : tweet['retweet_count'],
                    'reply_count'  :tweet['reply_count'],
                    'source' : tweet['tweet_source'],
                    'user_followers' : tweet['user_followers'],
                    'user_name' : tweet['user_name'],
                    'user_id' : tweet['user_id'],
                    })
            print("tweet has: ",tweet['trend'])
            print("td has",td[tweet['trend']])

            Trend.add_tweet(new_tweet,td[tweet['trend']])
        
            updated.append(new_tweet)

        except BaseException as e:
            print('stream tweet creation failed,',str(e))

    return updated






def get_location_object(location):
    try:
        location_ob, loc_created = Location.objects.get_or_create(
                    location = location
                )
        if loc_created == True:
            location_ob.save()
        return location_ob,loc_created
    except BaseException as e:
        print('error: on_update_trends', str(e))


def get_default_location():
    try:
        location, loc_created = Location.objects.get_or_create(
                    location = 'Worldwide'
                )
        if loc_created == True:
            location.save()
        
        return location
    except BaseException as e:
        print('error: on_user_update_trends', str(e))

def get_trend_from_query(query):
    try:
        trend_query_object = Trend.objects.get(name = query)
        return trend_query_object
    except:
        print("error: get_trend_from_query(), failed to get trend_query_objects, it might be because trend does not exist")


class TrendViewSet(viewsets.ModelViewSet):

    queryset = Trend.objects.all()
    serializer_class = TrendSerializer
    permission_classes = [permissions.IsOwnerOrReadOnly]

    


    # @method_decorator(cache_page(60*60*2))
    def list(self, request, *args, **kwargs):
        try:
            limit = int(request.GET.get('limit',-1))
            location = request.GET.get('location','Worldwide')
  

            if limit == -1:
                queryset = Trend.objects.filter(is_active = 1, locations__location__in = [location]).order_by('-volume')
            else:
                queryset = Trend.objects.filter(is_active = 1, locations__location__in = [location]).order_by('-volume')[:limit]

            serializer = TrendSerializer(queryset, many=True,context={'request': request})

        except BaseException as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data)

    def create(self, request,*args,**kwargs):
    
        data = request.data
        keys = ['slug','volume']
        if hasattr(data,'_mutable'):
            data._mutable=True
        for key in keys:
            if key not in data.keys():
                data[key] = None

        was_created = False

        try:
            new_trend, created = Trend.objects.get_or_create(
                name=data['name'],
                defaults={
                            'slug': data['slug'],
                            'volume': data['volume'],
                            'is_user_trend':1
                            })
            if created == True:
                was_created=True
                new_trend.save()

            if request.user not in new_trend.users.all():
                Trend.add_user(request.user, new_trend)

        except BaseException as e:
            print('creation failed,',str(e))

        serializer = TrendSerializer(new_trend, context = {'request':request,'was_created':was_created})
        return Response(serializer.data)

    def create_object(self,trend):
        try:
            new_trend, created = Trend.objects.get_or_create(
                    name=trend['key'],
                    defaults={
                            'is_user_trend': 1,
                            'is_active':1
                            })

            return new_trend,created
        except BaseException as e:
            print("error: TrendViewSet->create_object, ", str(e))

    def create_base_trend_object(self,trend):
        try:
            new_trend, created = Trend.objects.get_or_create(
                        name=trend['name'],
                        defaults={
                            'slug':  trend['url'],
                            'volume':trend['tweet_volume'],
                            'is_user_trend': 0,
                            'is_active':1
                            })
            return new_trend,created
        except BaseException as e:
            print("error: TrendViewSet->create_base_trend_object, ", str(e))
    
    def on_create_user_trends(self,user,trends):
        updated_trends = []
        
        location = get_default_location()

        for trend in trends:
            try:
                new_trend,created = self.create_object(trend)

                if created == True:
                    updated_trends.append(new_trend)

                if user not in new_trend.users.all():
                    Trend.add_user(user, new_trend)
                if location not in new_trend.locations.all():
                    Trend.add_location(location,new_trend)

            except BaseException as e:
                print('error: on_create_user_trends',str(e))

        return updated_trends

    @action(detail=False, methods=['post','get'])
    def create_user_trends(self, request, *args, **kwargs):


        data = request.data['query']
        updated_trends = self.on_create_user_trends(request.user,data)

        queryset = updated_trends
        serializer = TrendSerializer(data=queryset,many=True,context={'request': request})
        serializer.is_valid(raise_exception=False)
        serializer.save()

        return Response(serializer.data)

    def on_update_base_trends(self,trends):
        updated_trends={}

        for trend_object in trends:
            location_name = trend_object[3][0]['name']
            location,loc_created = get_location_object(location_name)

            trend_objects = []

            for place_trend in trend_object[0]:
                    try: 
                        new_trend,created = self.create_base_trend_object(place_trend)
                        if created == True:
                            trend_objects.append(new_trend)
                        else:
                            new_trend.is_active = 1
                            new_trend.save()
                        # if user not in new_trend.users.all():
                        #     Trend.add_user(user, new_trend)
                        if location not in new_trend.locations.all():
                            Trend.add_location(location,new_trend)

                    except BaseException as e:
                        print('trend creaton failed,',str(e))
            updated_trends[location_name] = trend_objects   

        return updated_trends

    @transaction.atomic
    def reset_active(self):
        trends = Trend.objects.all()
        for trend in trends:
            trend.is_active = False
            trend.save()


    def update_base_trends(self):

        crawler = CrawlerViewSet()
        trends = crawler.get_trends(LOCATIONS)
        self.reset_active()
        updated_trends = self.on_update_base_trends(trends)
        
        return updated_trends
        # queryset = updated_trends
        # serializer = TrendSerializer(data=queryset,many=True,context={'request': request})
        # serializer.is_valid(raise_exception=False)
        # serializer.save()

        # return Response(serializer.data)


    @action(detail=True, methods=['get','post'])
    def topics(self,request, pk = None):
        trend = Trend.objects.get(pk= pk)


        key = 'trend_topics' + str(trend.id)

        if cache.has_key(key):
            return Response(cache.get(key))
        else:
            tweet_set = list(trend.tweets.all().values('text'))

            topic_modelling_obj = TopicModelling(tweet_set)


            topics = topic_modelling_obj.getTopics()

            topic_cache = cache.set(key,topics, 60*60)

        return Response(topics)


    @action(detail=True, methods=['get','post'])
    def reset_cache_topics(self,request, pk = None):
        
        trend = Trend.objects.get(pk= pk)

        key = 'trend_topics' + str(trend.id)

        if cache.has_key(key):
            cache.delete(key)
            return Response({'status':'cache cleared'})
        return Response({'status':'cache key not found'})
        

    # @action(detail=True, methods=['get','post'])
    # def tweet_count(self,request, pk = None):
    #     trend = Trend.objects.get(pk=pk)    
    #     return Response({'tweet_count':trend.tweets.all().count()})


    @action(detail=True, methods=['get','post'])
    def rankings(self,request, pk = None):
        trend = Trend.objects.get(pk = pk)
        tweet_set = trend.tweets.all()

        result = rankings.contributer_data(tweet_set)

        tweet_count = tweet_set.count()

        result['tweet_count'] = tweet_count




        return Response(result)
    
    

    @action(detail=True, methods=['get'])
    def sentiment(self,request, pk = None):

        trend = Trend.objects.get(pk = pk)
        tweet = trend.tweets.last()

        tweet_key = 'last_tweet_of' + str(trend.id)
        key = 'sentiment' + str(trend.id)

        if cache.has_key(tweet_key):
            tweet_key_val = cache.get(tweet_key)
            if tweet_key_val != tweet.id:
                cache.set(tweet_key,tweet.id,60*60)
                cache.delete(key)
        else:
            cache.set(tweet_key,tweet.id,60*60)

        if cache.has_key(key):
            return Response(cache.get(key))
        else:
        # dummy_tweet = trend.tweets.all()
        # if len(dummy_tweet) == 0:
        #     return Response({'error': 'zero tweets'})
        # dummy_tid = dummy_tweet[0].tid

            try:
                sentiment_obj,created = TrendSentiment.objects.get_or_create(trend = trend,
                defaults = {
                    'pos_pol_count': 0,
                    'neg_pol_count' : 0,
                    'neu_pol_count':0,
                    'sub_count':0,
                    'obj_count':0,
                    'calculated_upto':0,
                    # 'top_pos_1':dummy_tid,
                    # 'top_pos_2':dummy_tid,
                    # 'top_pos_3':dummy_tid,
                    # 'top_neg_1':dummy_tid,
                    # 'top_neg_2':dummy_tid,
                    # 'top_neg_3':dummy_tid,
                    # 'top_neu_1':dummy_tid,
                    # 'top_neu_2':dummy_tid,
                    # 'top_neu_3':dummy_tid,
                })
            except Exception as e:
                print("error in TrendViewset, sentiment:" + str(e))

            calculated_upto = sentiment_obj.calculated_upto

            tweet_set = trend.tweets.filter(pk__gt=calculated_upto)

            print(tweet_set)

            tweet_set_count = tweet_set.count()

            print(tweet_set_count)

            # return Response({'tweet_set_count': tweet_set_count})

            last = None
            # last = tweet_set[len(tweet_set) - 1] if tweet_set else None
            
            if tweet_set_count > 0:
                last = tweet_set[tweet_set_count - 1]
            
                res_dict,tops = sentiment.get_sentiment_data(tweet_set)
                # print(res_dict)
                # print(tops)
                if last is not None:
                    sentiment_obj.calculated_upto = last.id

                sentiment_obj.pos_pol_count += res_dict['pos_pol_count']
                sentiment_obj.neg_pol_count += res_dict['neg_pol_count']
                sentiment_obj.neu_pol_count += res_dict['neu_pol_count']
                sentiment_obj.sub_count += res_dict['sub_count']
                sentiment_obj.obj_count += res_dict['obj_count']

                if created:
                    if tops['top_pos_1'] is not None:
                        sentiment_obj.top_pos_1 = tops['top_pos_1'].tid
                    if tops['top_pos_2'] is not None:
                        sentiment_obj.top_pos_2 = tops['top_pos_2'].tid
                    if tops['top_pos_3'] is not None:
                        sentiment_obj.top_pos_3 = tops['top_pos_3'].tid
                    if tops['top_neg_1'] is not None:
                        sentiment_obj.top_neg_1 = tops['top_neg_1'].tid
                    if tops['top_neg_2'] is not None:
                        sentiment_obj.top_neg_2 = tops['top_neg_2'].tid
                    if tops['top_neg_3'] is not None:
                        sentiment_obj.top_neg_3 = tops['top_neg_3'].tid
                    if tops['top_neu_1'] is not None:
                        sentiment_obj.top_neu_1 = tops['top_neu_1'].tid
                    if tops['top_neu_2'] is not None:
                        sentiment_obj.top_neu_2 = tops['top_neu_2'].tid
                    if tops['top_neu_3'] is not None:
                        sentiment_obj.top_neu_3 = tops['top_neu_3'].tid
                else:
                    top_tweet_pos_1 = top_tweet_pos_2 = top_tweet_pos_3 = None
                    top_tweet_neg_1 = top_tweet_neg_2 = top_tweet_neg_3 = None
                    top_tweet_neu_1 = top_tweet_neu_2 = top_tweet_neu_3 = None

                    try:
                        Tweet.objects.get(tid = sentiment_obj.top_pos_1)
                        top_tweet_pos_1 = Tweet.objects.get(tid = sentiment_obj.top_pos_1)
                        if tops['top_pos_1'] is not None and top_tweet_pos_1.like_count < tops['top_pos_1'].like_count:
                            sentiment_obj.top_pos_1 = tops['top_pos_1'].tid
                    except Tweet.DoesNotExist:
                        pass
                    try:
                        Tweet.objects.get(tid = sentiment_obj.top_pos_2)
                        top_tweet_pos_2 = Tweet.objects.get(tid = sentiment_obj.top_pos_2)
                        if tops['top_pos_2'] is not None and top_tweet_pos_2.like_count < tops['top_pos_2'].like_count:
                            sentiment_obj.top_pos_2 = tops['top_pos_2'].tid
                    except Tweet.DoesNotExist:
                        pass
                    try:
                        Tweet.objects.get(tid = sentiment_obj.top_pos_3)
                        top_tweet_pos_3 = Tweet.objects.get(tid = sentiment_obj.top_pos_3)
                        if tops['top_pos_3'] is not None and top_tweet_pos_3.like_count < tops['top_pos_3'].like_count:
                            sentiment_obj.top_pos_3 = tops['top_pos_3'].tid
                    except Tweet.DoesNotExist:
                        pass

                    try:
                        Tweet.objects.get(tid = sentiment_obj.top_neg_1)
                        top_tweet_neg_1 = Tweet.objects.get(tid = sentiment_obj.top_neg_1)
                        if tops['top_neg_1'] is not None and top_tweet_neg_1.like_count < tops['top_neg_1'].like_count:
                            sentiment_obj.top_neg_1 = tops['top_neg_1'].tid
                    except Tweet.DoesNotExist:
                        pass
                    try:
                        Tweet.objects.get(tid = sentiment_obj.top_neg_2)
                        top_tweet_neg_2 = Tweet.objects.get(tid = sentiment_obj.top_neg_2)
                        if tops['top_neg_2'] is not None and top_tweet_neg_2.like_count < tops['top_neg_2'].like_count:
                            sentiment_obj.top_neg_1 = tops['top_neg_1'].tid
                    except Tweet.DoesNotExist:
                        pass
                    try:
                        Tweet.objects.get(tid = sentiment_obj.top_neg_3)
                        top_tweet_neg_3 = Tweet.objects.get(tid = sentiment_obj.top_neg_3)
                        if tops['top_neg_3'] is not None and top_tweet_neg_3.like_count < tops['top_neg_3'].like_count:
                            sentiment_obj.top_neg_3 = tops['top_neg_3'].tid
                    except Tweet.DoesNotExist:
                        pass
                    try:
                        Tweet.objects.get(tid = sentiment_obj.top_neu_1)
                        top_tweet_neu_1 = Tweet.objects.get(tid = sentiment_obj.top_neu_1)
                        if tops['top_neu_1'] is not None and top_tweet_neu_1.like_count < tops['top_neu_1'].like_count:
                            sentiment_obj.top_neu_1 = tops['top_neu_1'].tid
                    except Tweet.DoesNotExist:
                        pass
                    try:
                        Tweet.objects.get(tid = sentiment_obj.top_neu_2)
                        top_tweet_neu_2 = Tweet.objects.get(tid = sentiment_obj.top_neu_2)
                        if tops['top_neu_2'] is not None and top_tweet_neu_2.like_count < tops['top_neu_2'].like_count:
                            sentiment_obj.top_neu_2 = tops['top_neu_2'].tid
                    except Tweet.DoesNotExist:
                        pass
                    try:
                        Tweet.objects.get(tid = sentiment_obj.top_neu_3)
                        top_tweet_neu_3 = Tweet.objects.get(tid = sentiment_obj.top_neu_3)
                        if tops['top_neu_3'] is not None and top_tweet_neu_3.like_count < tops['top_neu_3'].like_count:
                            sentiment_obj.top_neu_3 = tops['top_neu_3'].tid
                    except Tweet.DoesNotExist:
                        pass

                sentiment_obj.save()


            res = {
                    "id":sentiment_obj.id,
                    "pos_pol_count": sentiment_obj.pos_pol_count,
                    "neg_pol_count": sentiment_obj.neg_pol_count,
                    "neu_pol_count": sentiment_obj.neu_pol_count,
                    "sub_count": sentiment_obj.sub_count,
                    "obj_count": sentiment_obj.obj_count,
                    "calculated_upto": sentiment_obj.calculated_upto,
                    "top_pos_1": str(sentiment_obj.top_pos_1),
                    "top_pos_2": str(sentiment_obj.top_pos_2),
                    "top_pos_3": str(sentiment_obj.top_pos_3),
                    "top_neg_1": str(sentiment_obj.top_neg_1),
                    "top_neg_2": str(sentiment_obj.top_neg_2),
                    "top_neg_3": str(sentiment_obj.top_neg_3),
                    "top_neu_1": str(sentiment_obj.top_neu_1),
                    "top_neu_2": str(sentiment_obj.top_neu_2),
                    "top_neu_3": str(sentiment_obj.top_neu_3)
                }
            sentiment_cache = cache.set(key,res, 60*60)
    
        # serializer = TrendSentimentSerializer(sentiment_obj,context={'request': request})
        return Response(res)


    @action(detail=True, methods=['get'])
    def get_stats(self,request, pk = None):
    
        trend = Trend.objects.get(pk = pk)
        try:
            trend_stats,created = TrendStats.objects.get_or_create(trend = trend,
            defaults = {
                'like_count': 0,
                'reply_count' : 0,
                'retweet_count':0,
                'min_followers':0,
                'max_followers':0,
                'average_followers': 0,
                'calculated_upto':0,
            })
        except Exception as e:
            print("error in TrendViewset, get_stats:" + str(e))

        calculated_upto = trend_stats.calculated_upto

        tweet_set = trend.tweets.filter(pk__gt=calculated_upto)
        if tweet_set:
            last = tweet_set[len(tweet_set) - 1] if tweet_set else None
            source_dict,public_dict,user_dict = metrics.get_tweet_info(tweet_set)

            trend_stats.like_count += public_dict['like']
            trend_stats.retweet_count+= public_dict['retweet']
            trend_stats.reply_count+= public_dict['reply']
            trend_stats.min_followers += user_dict['min_followers']
            trend_stats.max_followers+= user_dict['max_followers']
            trend_stats.average_followers += user_dict['avg_followers']

            if last is not None:
                trend_stats.calculated_upto = last.id

            trend_stats.save()


            for key in source_dict.keys():
                try:
                    trend_source,created = TrendSources.objects.get_or_create(source_name = key, trend_stats = trend_stats,
                    defaults = {
                        'count':source_dict[key],
                    })

                    if not created:
                        trend_source.count += source_dict[key]
                        trend_source.save()

                except BaseException as e:
                    print("error in TrendViewset, get_stats:" + str(e))

        
        sources = trend_stats.trend_sources.all()
        src_dict = {}
        for source in sources:
            src_dict[source.source_name] = source.count

        pub = {}
        pub['like_count'] = trend_stats.like_count
        pub['retweet_count'] = trend_stats.retweet_count
        pub['reply_count']= trend_stats.reply_count
        user = {}
        user['min_followers'] = trend_stats.min_followers
        user['max_followers'] = trend_stats.max_followers
        user['avg_followers']= trend_stats.average_followers

        data_dict = {
            'source':src_dict,
            'public':pub,
            'user':user
        }
        return Response(data_dict)

    @action(detail=False, methods=['get','post'])
    def get_user_trends(self,request):
        user_trend = Trend.objects.filter(users=request.user)
        queryset = user_trend
        serializer = TrendSerializer(data=queryset,many=True,context={'request': request})
        serializer.is_valid(raise_exception=False)
        serializer.save()
        return Response(serializer.data)


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
class TrendSentimentViewSet(viewsets.ModelViewSet):
    queryset = TrendSentiment.objects.all()
    serializer_class = TrendSentimentSerializer

class TrendStatsViewSet(viewsets.ModelViewSet):
    queryset = TrendStats.objects.all()
    serializer_class = TrendStatsSerializer

class TrendSourcesViewSet(viewsets.ModelViewSet):
    queryset = TrendSources.objects.all()
    serializer_class = TrendSourcesSerializer

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class GeoPlacesViewSet(viewsets.ModelViewSet):
    queryset = GeoPlaces.objects.all()
    serializer_class = GeoPlacesSerializer

class TweetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer


    def list(self, request, *args, **kwargs):
        try:
            limit = int(request.GET.get('limit',-1))
      
            if limit == -1:
                queryset = Tweet.objects.all()[:50]
            else:
                queryset = Tweet.objects.all()[:limit]
            serializer = TweetSerializer(queryset, many=True,context={'request': request})

            return Response(serializer.data)

        except BaseException as e:
            print('limit not found',str(e))

        return Response({'error':'some kind of exception'})

    
    def create_object(self,tweet):
        pass
    
    @transaction.atomic
    def bulk_create_objects(self,tweets,trend):


        tweets_created = list()
        # for tweet in tweets:
        #     tweet_obj = Tweet(tid = tweet['id'],text = tweet['text'],like_count =tweet['likes'],retweet_count = tweet['retweet_count'],
        #     reply_count =tweet['reply_count'],source = tweet['tweet_source'],user_followers= tweet['user_followers'],
        #     user_name = tweet['user_name'],user_id = tweet['user_id'])
        #     tweets_created.append(tweet_obj)

        # objs = Tweet.objects.bulk_create(tweets_created, ignore_conflicts=True)
            
        for tweet in tweets:
            
            new_tweet,created  = Tweet.objects.get_or_create(tid = tweet['id'],
                defaults = {
    
                    'text' : tweet['text'],
                    'like_count' :tweet['likes'],
                    'retweet_count' : tweet['retweet_count'],
                    'reply_count'  :tweet['reply_count'],
                    'source' : tweet['tweet_source'],
                    'user_followers' : tweet['user_followers'],
                    'user_name' : tweet['user_name'],
                    'user_id' : tweet['user_id'],
                    })

            if created:
                tweets_created.append(new_tweet)
                Trend.add_tweet(new_tweet,trend)
            else:
                Trend.add_tweet_2(new_tweet,trend)


        return tweets_created

    #MAKE THIS MULTITHREADED.
    def on_create_tweets(self,tweets):

        tweets_created = {}
        for key in tweets.keys():
            key_tweets = tweets[key]['tweets']
            key_includes = tweets[key]['includes']
            trend = get_trend_from_query(key)
            tweets_created[key] = self.bulk_create_objects(key_tweets,trend)
        
        return tweets_created

    @action(detail=False, methods=['post','get'])
    def create_tweets(self,request):

        query = request.data.get('query')
        crawler_id = request.data.get('crawler')

        crawler = CrawlerViewSet()

        tweet_list = crawler.crawl_tweets(request)
        if tweet_list is None:
            return Response({'crawler returned None'})
        tweets = tweet_list.data

        tweets_created = self.on_create_tweets(tweets)

        response = {}
        for key in tweets_created.keys():
            response[key] = len(tweets_created[key]) 


        return Response(response)
        
    def base_create_tweets(self,query):
        crawler = CrawlerViewSet()

        tweet_list = crawler.base_crawl_tweets(query = query)
        if tweet_list is None:
            return Response({'crawler returned None'})
        tweets = tweet_list

        tweets_created = self.on_create_tweets(tweets)

        response = {}
        for key in tweets_created.keys():
            response[key] = len(tweets_created[key]) 
        return response


    '''
    STREAM ENDPOINTS
    '''
    @action(detail=False, methods=['get','post'])
    def stream_create_tweets(self,request):
        crawler_viewset = CrawlerViewSet()
        stream_object = crawler_viewset.stream_crawl_tweets(request)
        return stream_object
    



@api_view(['GET', 'POST'])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAuthenticated])
def user_stream_search(request):
   
    if request.method == 'POST':
        trendviewset = TrendViewSet()
        tweetviewset = TweetViewSet()
        ctresponse = trendviewset.create_user_trends(request)
        tresponse = tweetviewset.stream_create_tweets(request)

        response = dict()
        response['created_trends'] = ctresponse.data
        response['stream_response'] = tresponse.data

        return Response(response)

    return Response({'status':'error'})

@api_view(['GET', 'POST'])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAuthenticated])
def user_search(request):
   
    if request.method == 'POST':
        trendviewset = TrendViewSet()
        tweetviewset = TweetViewSet()
        ctresponse = trendviewset.create_user_trends(request)
        tresponse = tweetviewset.create_tweets(request)
        response = dict()
        response['created_trends'] = ctresponse.data
        response['tweets'] = tresponse.data

        return Response(response)

    return Response({'status':'error'})


def default_update():

    trendviewset = TrendViewSet()
    tweetviewset = TweetViewSet()
    updated_trends = trendviewset.update_base_trends()

    response = []

    for trend in updated_trends.keys():
        trends = updated_trends[trend]
        query = []
        for i in trends:
            d = dict()
            d['key'] = i.name
            d['max_results'] = 10
            d['count'] = 1
            query.append(d)

        res = tweetviewset.base_create_tweets(query = query)
        response.append({trend:res})

    return response



def default_delete():
    four_days_ago = timezone.now() - datetime.timedelta(days=4)
    Trend.objects.filter(trend_created__lte = four_days_ago).delete()



