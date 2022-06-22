import tweepy
import pandas as pd
import time
import datetime

from .. import views



class StreamListener(tweepy.StreamingClient):
    
    def __init__(self,bearer_token,stream_obj):

        self.bulk_response = []
        self.data = []
        self.start_time = None
        self.end_time = None

        self.elapsed = stream_obj.elapsed.seconds
        self.duration = stream_obj.duration.seconds
        self.stream_obj = stream_obj
        self.response_count = 1

        self.user = stream_obj.crawler.user

        super().__init__(bearer_token)

    #def on_tweet(self, tweet):
        #print(tweet.text)
    def on_connect(self):
        print("Connected to StreamingAPI, for user: ",self.user.username)
        self.start_time = time.time()
        self.stream_obj.is_running = 1
        
    def on_connection_error(self):
        self.end_time = time.time()
        self.elapsed = self.end_time - self.start_time
        self.stream_obj.elapsed= datetime.timedelta(seconds = self.elapsed)
        self.stream_obj.is_running = 0
        self.disconnect()
        
    def on_disconnect(self):
        self.end_time = time.time()
        self.elapsed = self.end_time - self.start_time
        self.stream_obj.elapsed= datetime.timedelta(seconds = self.elapsed)
        self.stream_obj.is_running = 0

        print("Disconnected from StreamingAPI after running for ",self.elapsed)

        views.stream_response(self.data)
        views.save_stream_object(self.stream_obj)

 
    def on_response(self,stream_response):
        # if self.stream_obj.is_running == 0:
        #     self.disconnect()
        self.elapsed = time.time() - self.start_time

        if self.elapsed >= self.duration:
            self.disconnect()

        # print('tweet response received')
        users = {u["id"]: u for u in stream_response.includes['users']}
        #print(stream_response.includes)
        user = users[stream_response.data.author_id]
        d = {'id':stream_response.data.id,'user_id':stream_response.data.author_id,'user_name':user.username,'text':stream_response.data.text,'trend':stream_response.matching_rules[0].tag,'likes':stream_response.data.public_metrics['like_count'],'tweet_source':stream_response.data.source,'user_followers':user.public_metrics['followers_count'],'retweet_count':stream_response.data.public_metrics['retweet_count'],'reply_count':stream_response.data.public_metrics['reply_count']}
        self.data.append(d)
        self.bulk_response.append(d)
        stream_data = {}
        stream_data['response_count'] = self.response_count
        stream_data['elapsed'] = self.elapsed
        stream_data['username'] = self.user.username
        stream_data['stream_obj'] = self.stream_obj

        if self.elapsed > 10* self.response_count:
            self.response_count = self.response_count +1
            views.stream_tweet_response(self.bulk_response,stream_data)
            self.bulk_response = []

    #def on_matching_rules(self,rule):
        #print(rule)

    def make_rules(self,trends):
        
        for name in trends:
            self.add_rules(tweepy.StreamRule(value = "("+ name +")"+" lang:en -is:retweet",tag = name))