import tweepy
import pandas as pd

from threading import Thread




class BatchCrawler(tweepy.Client):
    
    def __init__(self,key_dict):
        self.consumer_key = key_dict["consumer_key"]
        self.consumer_secret = key_dict["consumer_secret"]
        self.access_token = key_dict["access_token"]
        self.access_token_secret = key_dict["access_secret"]
        self.bearer_token = key_dict["bearer_token"]
        
        super().__init__(bearer_token=self.bearer_token,
                        consumer_key=self.consumer_key,
                        consumer_secret=self.consumer_secret,
                        access_token=self.access_token,
                        access_token_secret=self.access_token_secret)

    
    
    def crawl_tweets(self,trend_name,max_results=10,count = 1):
        tweet_list = []
        try:
            response = self.search_recent_tweets(trend_name+" lang:en -is:retweet -(😝 OR 🥰 OR 😈) -is:reply -has:media -has:links",max_results=max_results ,expansions=['author_id','geo.place_id'],tweet_fields = ['public_metrics','source','context_annotations','geo','created_at'],user_fields=['profile_image_url','public_metrics'],place_fields = ['country','geo'])
            users = {u["id"]: u for u in response.includes['users']}
            for tweet in response.data:
                user = users[tweet.author_id]
                tweet_dict = {'id':tweet['id'],'user_id':tweet.author_id,'user_name':user.username,'text':tweet['text'],'trend':trend_name,'likes':tweet.public_metrics['like_count'],'tweet_source':tweet.source,'user_followers':user.public_metrics['followers_count'],'retweet_count':tweet.public_metrics['retweet_count'],'reply_count':tweet.public_metrics['reply_count'],'created_at':tweet['created_at']}
                tweet_list.append(tweet_dict)
        except BaseException as e:
            print('Batch Crawler: failed on_status,',str(e))
            
        return tweet_list,response.includes
    
    def crawl_tweets2(self,trend_name,max_results=10,count = 1):
        tweet_list = []
        include_list ={}
        include_list['users'] = []
        include_list['places'] = []
        try:
            responses = tweepy.Paginator(self.search_recent_tweets, query=(trend_name+" lang:en -is:retweet -(😝 OR 🥰 OR 😈) -is:reply -has:media -has:links"),max_results=max_results,limit = count ,expansions=['author_id','geo.place_id'],tweet_fields = ['public_metrics','source','context_annotations','geo','created_at'],user_fields=['profile_image_url','public_metrics'],place_fields = ['country','geo'])
            for response in responses:
                users = {u["id"]: u for u in response.includes['users']}
                include_list['users'].append(response.includes['users'])
                if 'places' in response.includes.keys():
                    include_list['places'].append(response.includes['places'])
                for tweet in response.data:
                    user = users[tweet.author_id]
                    tweet_dict = {'id':tweet['id'],'user_id':tweet.author_id,'user_name':user.username,'text':tweet['text'],'trend':trend_name,'likes':tweet.public_metrics['like_count'],'tweet_source':tweet.source,'user_followers':user.public_metrics['followers_count'],'retweet_count':tweet.public_metrics['retweet_count'],'reply_count':tweet.public_metrics['reply_count'],'created_at':tweet['created_at']}
                    tweet_list.append(tweet_dict)
        except BaseException as e:
            print('Batch Crawler: failed on_status,',str(e))
            
        return tweet_list,include_list
    