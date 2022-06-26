from django.db import models



from user.models import CustomUser as User
# Create your models here.




class Location(models.Model):
    location = models.CharField(max_length=255, default=None)

class GeoPlaces(models.Model):
    place = models.CharField(max_length=255, default=None)

class Topic(models.Model):
    name = models.CharField(max_length=255,blank=True)


class Tweet(models.Model):
    text = models.CharField(max_length=280)
    tid = models.BigIntegerField(blank=True,null=True, unique=True)

    like_count =  models.BigIntegerField(blank=True,null=True)
    retweet_count =  models.BigIntegerField(blank=True,null=True)
    reply_count =  models.BigIntegerField(blank=True,null=True)

    source = models.CharField(max_length=255,blank=True)
    user_followers = models.IntegerField(blank=True,null=True)

    user_name = models.CharField(max_length=255, blank=True)
    user_id = models.BigIntegerField(blank=True,null=True)

    

class Trend(models.Model):

    name = models.CharField(max_length=255, blank = False , default ="lorem ipsum")
    slug = models.SlugField(max_length=255, blank=True)
    volume = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True, blank = True)
    as_of = models.DateTimeField(auto_now_add=True,blank=True)
    is_user_trend = models.IntegerField(default=0)
    is_active = models.IntegerField(default =1)

    tweets = models.ManyToManyField(Tweet,related_name='trend',blank = True, db_index=True)
    topics = models.ManyToManyField(Topic,related_name='trend',blank =True)
    locations = models.ManyToManyField(Location,related_name='trend',blank = True)
    geoplaces = models.ManyToManyField(GeoPlaces,related_name='trend',blank = True)
    users = models.ManyToManyField(User, related_name = 'trend',blank = True)


    def __str__(self):
        return self.name
    def add_user(user, trend):
        if user not in trend.users.all():
            trend.users.add(user)
    def remove_user(user, trend):
        trend.users.remove(user)   
    # adding tweet object to trend.
    def add_tweet(tweet,trend):
        trend.tweets.add(tweet)
    def add_tweet_2(tweet,trend):
        if tweet not in trend.tweets.all():
            trend.tweets.add(tweet)
    def remove_tweet(tweet,trend):
        trend.tweets.remove(tweet)
    # adding topic object to trend.
    def add_topic(topic,trend):
        trend.topics.add(topic)
    def remove_topic(topic,trend):
        trend.topics.remove(topic)
    def add_location(location,trend):
        trend.locations.add(location) 
    def remove_location(location,trend):
        trend.locations.remove(location)





#Models for optimizing the performance.

class TrendSentiment(models.Model):

    pos_pol_count = models.IntegerField(null=True)
    neg_pol_count = models.IntegerField(null=True)
    neu_pol_count = models.IntegerField(null=True)

    sub_count = models.IntegerField(null=True)
    obj_count = models.IntegerField(null=True)

    calculated_upto = models.BigIntegerField(blank=True, null=True, db_index=True)

    top_pos_1 = models.BigIntegerField(blank=True, null=True) 
    top_pos_2 = models.BigIntegerField(blank=True, null=True) 
    top_pos_3 = models.BigIntegerField(blank=True, null=True) 
    top_neg_1 = models.BigIntegerField(blank=True, null=True) 
    top_neg_2 = models.BigIntegerField(blank=True, null=True) 
    top_neg_3 = models.BigIntegerField(blank=True, null=True) 
    top_neu_1 = models.BigIntegerField(blank=True, null=True) 
    top_neu_2 = models.BigIntegerField(blank=True, null=True) 
    top_neu_3 = models.BigIntegerField(blank=True, null=True) 

    trend = models.OneToOneField(Trend, on_delete=models.CASCADE, null=True)


class TrendStats(models.Model):

    like_count = models.IntegerField(null=True)
    reply_count = models.IntegerField(null=True)
    retweet_count = models.IntegerField(null=True)

    min_followers = models.IntegerField(null=True)
    max_followers = models.IntegerField(null=True)
    average_followers = models.IntegerField(null=True)

    calculated_upto = models.BigIntegerField(blank=True, null=True)

    trend = models.OneToOneField(Trend, on_delete=models.CASCADE, null=True)



class TrendSources(models.Model):
    source_name = models.CharField(max_length=255, null=True)
    count = models.IntegerField(null=True)
    trend_stats = models.ForeignKey(TrendStats,related_name = "trend_sources",on_delete= models.CASCADE, null=True, blank=True)