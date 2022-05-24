import abc
import tweepy
from operator import itemgetter
import pandas as pd


class BaseCrawler:
    def __init__(self,key_dict):
        self.consumerKey = key_dict["consumer_key"]
        self.consumerSecret = key_dict["consumer_secret"]
        self.accessToken = key_dict["access_token"]
        self.accessTokenSecret = key_dict["access_token_secret"]
        self.bearer_token = key_dict["bearer_token"]

        self.saved_available_trends = []
        self.saved_place_trends = []

        try:
            self.auth = tweepy.OAuthHandler(self.consumerKey, self.consumerSecret)
            self.auth.set_access_token(self.accessToken,self.accessTokenSecret)
            self.api = tweepy.API(self.auth,wait_on_rate_limit=True)
            self.api.verify_credentials()
        except :
            print('auth error')
    
    def get_available_trends(self):
        self.saved_available_trends = self.api.available_trends()
        return self.saved_available_trends
    
    def get_place_trends(self,WOEID=1,count=10):
        if count > 10:
            print("trend count cannot be more than 10")
            return
        
        trends = self.api.get_place_trends(WOEID)
        
        trends_as_of = trends[0]['as_of']
        trends_created_at = trends[0]['created_at']
        trends_location = trends[0]['locations']

        trends = trends[0]['trends']
        trends = filter(itemgetter("tweet_volume"), trends)
        trends = list(trends)
        trends = sorted(trends, key = itemgetter('tweet_volume'),reverse = True)
        trends = trends[:count]
        
        self.saved_place_trends = [trends,trends_as_of,trends_created_at,trends_location]
        return self.saved_place_trends


            