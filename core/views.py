from collections import UserString
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes,throttle_classes
from rest_framework.throttling import UserRateThrottle


from .models import Topic, Trend, Tweet ,Location,GeoPlaces
from. models import User
from .serializers import TweetSerializer,TrendSerializer, TopicSerializer, LocationSerializer,GeoPlacesSerializer
from rest_framework.permissions import IsAuthenticated , IsAdminUser
from .import permissions

from crawler.views import CrawlerViewSet

from django.db import transaction
import concurrent.futures
import datetime
from django.utils import timezone
from .constants import LOCATIONS

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# Create your views here.



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
    permission_classes = [IsAuthenticated,permissions.IsOwnerOrReadOnly]


    @method_decorator(cache_page(60*60*2))
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


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

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

    
    def create_object(self,tweet):
        pass
    
    @transaction.atomic
    def bulk_create_objects(self,tweets,trend):

        tweets_created = []
        for tweet in tweets:
            try:
                new_tweet = Tweet.objects.create(
                    text = tweet['text'],
                    tid=tweet['id'],
                    like_count=tweet['likes'],
                    retweet_count = tweet['retweet_count'],
                    reply_count = tweet['reply_count'],
                    source = tweet['tweet_source'],
                    user_followers = tweet['user_followers'],
                    user_name = tweet['user_name'],
                    user_id = tweet['user_id'])
        
                tweets_created.append(new_tweet)
                Trend.add_tweet(new_tweet,trend)

            except BaseException as e:
                print('tweet creation failed,',str(e))

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
    def create_tweets(self,request, *args, **kwargs):
        query = request.data.get('query')
        crawler_id = request.data.get('crawler')

        crawler = CrawlerViewSet()

        tweet_list = crawler.crawl_tweets(request = request)
        if tweet_list is None:
            return Response({'crawler returned None'})
        tweets = tweet_list.data

        tweets_created = self.on_create_tweets(tweets)

        response = {}
        for key in tweets_created.keys():
            response[key] = len(tweets_created[key]) 


        return Response(response)
        
    def create_tweets(self,query):

        crawler = CrawlerViewSet()

        tweet_list = crawler.crawl_tweets(query = query)
        if tweet_list is None:
            return Response({'crawler returned None'})
        tweets = tweet_list

        tweets_created = self.on_create_tweets(tweets)

        response = {}
        for key in tweets_created.keys():
            response[key] = len(tweets_created[key]) 
        return response





@api_view(['GET', 'POST'])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAuthenticated])
def foo(request):

    if request.method == 'GET':
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

        res = tweetviewset.create_tweets(query = query)
        response.append({trend:res})

    return response



def default_delete():
    four_days_ago = timezone.now() - datetime.timedelta(days=4)
    Trend.objects.filter(trend_created__lte = four_days_ago).delete()

