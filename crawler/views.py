from django.shortcuts import render
from django.http import HttpResponse
from django.db import DatabaseError
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated , IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action

from .crawlers.base_crawler import BaseCrawler
from .crawlers.batch_crawler import BatchCrawler
from .crawlers.stream_crawler import StreamListener
from django.shortcuts import get_object_or_404

from .models import Crawler,StreamData
from .serializers import CrawlerSerializer,StreamDataSerializer
# Create your views here.
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


from .consumers import ChatConsumer

from . import utils
import datetime

import concurrent.futures
from user.views import get_admin_user

import json

'''HELPER FUCNTIONS
'''
def stream_tweet_response(tweets,stream_data):
    from core.views import stream_tweet_response as core_s_t_r

    stream_obj = stream_data['stream_obj']

    ret = core_s_t_r(tweets, stream_obj)



    channel_layer = get_channel_layer()
    message = {
        'text':str(len(ret)) + 'tweets have been stored.',
        'stream_obj_id':stream_obj.id,
        'response_count':stream_data['response_count'],
        'elapsed':stream_data['elapsed']
    }
    async_to_sync(channel_layer.group_send)(stream_data['username'], {"type": "chat_message","message":json.dumps(message)})

def stream_response(data):
    #logic here

    print("DATA RECIVED")
    pass
    
def save_stream_object(stream_obj):
    stream_obj.save()
    print("Stream obj recived and saved")

def lobby(request):
    return render(request,'test/lobby.html')


def get_all_rule_ids(stream_listener):

    if stream_listener is None:
        print("got a Nonetype stream_listener object")

    rules = stream_listener.get_rules()

    if rules.data is None:
        return

    ids = []
    for rule in rules.data:
        ids.append(rule.id)

    return ids


def get_crawler_instance(user,crawler_id=1):

    crawler_instance = None
    try:
        crawler_instances = Crawler.objects.filter(user=user)
        if len(crawler_instances) > 0:
            crawler_id = int(crawler_id)
            crawler_id = utils.clamp(crawler_id,1,len(crawler_instances))
            crawler_instance = crawler_instances[crawler_id-1]

    except BaseException as e:
        print("failed to get crawler instance")

    return crawler_instance


'''VIEWSETS'''

class CrawlerViewSet(viewsets.ModelViewSet):
    queryset = Crawler.objects.all()
    serializer_class = CrawlerSerializer
    permission_classes = [IsAuthenticated]


    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)


    def list(self, request, *args, **kwargs):

        queryset = Crawler.objects.filter(user=request.user)
        serializer = CrawlerSerializer(queryset, many=True , context={'request': request})

        return Response(serializer.data)

    def on_get_trends(self,base_crawler,woeids):

        trends = []
        for woeid in woeids:
            place_trends = base_crawler.get_place_trends(woeid)
            trends.append(place_trends)

        return trends

    def get_trends(self,locations):

        user = get_admin_user()

        try:
            crawler_instance = get_crawler_instance(user)
            print(crawler_instance)
            if crawler_instance is None:
                return Response({'error':'user does not own a crawler instance'})
        except:
            return Response({'error':'get_trends, failed to get crawler instance'})


        if crawler_instance is not None:
            woeids = []
            try:
                api_keys = crawler_instance.get_keys()
                base_crawler = BaseCrawler(api_keys)
            except BaseException as e:
                print("failed to get base_crawler isntance")
                
            available_trends = base_crawler.get_available_trends()

            for available_trend in available_trends:
                if available_trend['name'] in locations:
                    woeids.append(available_trend['woeid'])

            trends = self.on_get_trends(base_crawler,woeids)      

            return trends
        else:
            return None



    def start_crawl(self,crawler,query,max_results,count):
        # max_results = utils.clamp(max_results,10,100)
        # print("started for "+ query)
        response,include = crawler.crawl_tweets2(trend_name = query, max_results = max_results,count=count)
        result = {}
        result['tweets'] = response
        result['includes'] = include
        return result

    def on_crawl_tweets(self,batch_crawler,keyword_query_list):

        if keyword_query_list is None:
            return

        b_c = batch_crawler

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.start_crawl,b_c, keyword['key'],int(keyword['max_results']),int(keyword['count'])) for keyword in keyword_query_list]
            return_value = [f.result() for f in futures]

        result_dict = {}
        for idx,key in enumerate(keyword_query_list):
            # print(key['key'])
            result_dict[key['key']] = return_value[idx]

        return result_dict
    
    @action(detail=False, methods=['get','post'])
    def crawl_tweets(self,request):
        '''
        Private view to crawl tweets.
        '''

        if 'crawler' not in request.data.keys():
            print("crawler information missing")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            crawler_information = request.data['crawler']

        crawler_id = int(crawler_information["id"])
        
        crawler_instance = get_crawler_instance(request.user,crawler_id)
        if crawler_instance is None:
            return Response([{'error': 'failed to get crawler instance'}])

        api_keys = crawler_instance.get_keys()
        try:
            batch_crawler = BatchCrawler(api_keys)
        except:
            print("error: on_crawl_tweets(), batch_crawler instantiation failed")

        keyword_query_list = []

        if 'query' in request.data.keys():
            keyword_query_list = request.data['query']
        else:
            print("no query supplied in request")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        queryset = []
        queryset = self.on_crawl_tweets(batch_crawler,keyword_query_list)

        return Response(queryset)

    def base_crawl_tweets(self,query):

        '''
        Private view to crawl tweets.
        '''
        user = get_admin_user()
        crawler_instance = get_crawler_instance(user)
        if crawler_instance is None:
            return Response([{'error': 'failed to get crawler instance'}])

        api_keys = crawler_instance.get_keys()
        try:
            batch_crawler = BatchCrawler(api_keys)
        except:
            print("error: on_crawl_tweets(), batch_crawler instantiation failed")

        queryset = []
        queryset = self.on_crawl_tweets(batch_crawler,query)

        return queryset

    @action(detail=False, methods=['get'])
    def key_crawl_tweets(self,request):
        '''
        Public endpoint that requires a set of API keys to be provided along with the query and returns data.
        '''

        if 'api_keys' not in request.data.keys():
            print("Api keys are missing")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            api_keys = request.data['api_keys']
        try:
            batch_crawler = BatchCrawler(api_keys)
        except:
            print("error: on_crawl_tweets(), batch_crawler instantiation failed")

        keyword_query_list = []

        if 'query' in request.data.keys():
            keyword_query_list = request.data['query']
        else:
            print("no query supplied in request")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        queryset = []
        queryset = self.on_crawl_tweets(batch_crawler,keyword_query_list)

        return Response(queryset)
    
    def on_stream_crawl_tweets(self,stream_listener):

        #set rules for stream listener
        #keep previous rules or delete them????
        ids = get_all_rule_ids(stream_listener)
        if ids is not None:
            stream_listener.delete_rules(ids)
        #tbd
        query = stream_listener.stream_obj.get_query()
        keys = query.split(',')
        print("KEYS",keys)
        stream_listener.make_rules(keys)
        
        try:
            stream_listener.filter(threaded=True,expansions=['author_id','geo.place_id'],tweet_fields = ['public_metrics','source','context_annotations'],user_fields=['profile_image_url','public_metrics'],place_fields = ['country','geo'])
        except:
            print("error: on_stream_crawl_tweets(), during filter")

        #tweet dictionary will be maintained as an attribute of stream_listener.       
        return stream_listener.stream_obj

    @action(detail=False, methods=['get','post'])
    def stream_crawl_tweets(self,request):

        if 'crawler' not in request.data.keys():
            print("crawler information missing")
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            crawler_information = request.data['crawler']
        crawler_id = int(crawler_information["id"])
        crawler_duration = int(crawler_information["duration"]) * 60
        
        crawler_instance = get_crawler_instance(request.user,crawler_id)
        api_keys = crawler_instance.get_keys()


        if 'query' in request.data.keys():
            trend_query_list = request.data['query']
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        query = request.data['query']
        query = ','.join(i['key'] for i in query)

        try:
            stream_data_obj = StreamData.objects.create( crawler = crawler_instance,
                is_running = 0,
                query = query,
                duration=datetime.timedelta(seconds = crawler_duration),
                elapsed= datetime.timedelta())

            stream_data_obj.save()
        except:
            print("error: stream_crawl_tweets(), streamData instantiation failed")
            
        try:
            stream_listener = StreamListener(api_keys['bearer_token'],stream_data_obj)
        except BaseException as e:
            print("error: stream_crawl_tweets(), stream_listener instantiation failed" + str(e))

        stream_obj = self.on_stream_crawl_tweets(stream_listener)
                
        serializer = StreamDataSerializer(stream_obj,many=False,context={'request': request})
        return Response(serializer.data)


class StreamDataViewSet(viewsets.ModelViewSet):
    queryset = StreamData.objects.all()
    serializer_class = StreamDataSerializer
    permission_classes = [IsAuthenticated]

    # @action(detail=True, methods=['get','post'])
    # def stop_stream(self,request,pk = None):

    #     stream_obj = StreamData.objects.get(pk = pk)
    #     stream_obj.is_running = 0
    #     stream_obj.save()

    #     serializer = StreamDataSerializer(stream_obj,many=False,context={'request': request})
    #     return Response(serializer.data)
        


    