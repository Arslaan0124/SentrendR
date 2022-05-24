from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated , IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from .crawlers.batch_crawler import BatchCrawler
from .models import Crawler,StreamData
from .serializers import CrawlerSerializer,StreamDataSerializer
# Create your views here.

from . import utils

import concurrent.futures

'''HELPER FUCNTIONS
'''
def get_crawler_instance(user,crawler_id):

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

    def start_crawl(self,crawler,query,max_results,count):
        max_results = utils.clamp(max_results,10,100)
        count = utils.clamp(count,1,15)
        # print("started for "+ query)
        response,include = crawler.crawl_tweets(trend_name = query, max_results = max_results, count = count)
        result = {}
        result['tweets'] = response
        result['includes'] = include
        return result

    def on_crawl_tweets(self,batch_crawler,keyword_query_list):

        if keyword_query_list is None:
            return

        b_c = batch_crawler

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.start_crawl,b_c, keyword['key'],int(keyword['max_results']),int(keyword['count'])) for keyword in keyword_query_list]
            return_value = [f.result() for f in futures]

        result_dict = {}
        for idx,key in enumerate(keyword_query_list):
            print(key['key'])
            result_dict[key['key']] = return_value[idx]

        return result_dict



    @action(detail=False, methods=['get','post'])
    def crawl_tweets(self,request):

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

    
    @action(detail=False, methods=['get','post'])
    def key_crawl_tweets(self,request):

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
    

class StreamDataViewSet(viewsets.ModelViewSet):
    queryset = StreamData.objects.all()
    serializer_class = StreamDataSerializer
    permission_classes = [IsAuthenticated]