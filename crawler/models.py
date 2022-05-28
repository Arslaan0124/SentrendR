from django.db import models

# Create your models here.
from django.db import models
from datetime import datetime, timedelta 
from django.core.exceptions import ValidationError

from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_delete

from . import validators

from user.models import CustomUser
# Create your models here.



class Crawler(models.Model):

    user = models.ForeignKey(CustomUser,related_name='crawler',on_delete= models.CASCADE, null=True, blank=True)

    consumer_key = models.CharField(max_length=255,help_text="Consumer key of twitter API",null=False,default=None)
    consumer_secret = models.CharField(max_length=255,null=False,default=None,help_text="Consumer secret of twitter API")
    access_token = models.CharField(max_length=255,null=False,default=None,help_text="Access key of twitter API")
    access_secret = models.CharField(max_length=255,null=False,default=None,help_text="Consumer secret of twitter API")
    bearer_token = models.CharField(max_length=255,null=False,default=None,help_text="Bearer key of twitter API")


    def clean(self):
        #validate if the api keys are valid or not
        status = validators.validate_api_keys(self.consumer_key,self.consumer_secret,self.access_token,self.access_secret)

        if status == False:
            raise ValidationError('Model validation failed, incorrect API keys were provided')

    def save(self,*args,**kwargs):
        self.clean()
        super().save(*args,**kwargs)

    def __str__(self):
        return self.user.username

    def get_keys(self):
        '''Returns a dict of twitter API the keys'''
        keys_dict = {
            'consumer_key':self.consumer_key,
            'consumer_secret':self.consumer_secret,
            'access_token':self.access_token,
            'access_secret':self.access_secret,
            'bearer_token':self.bearer_token,
        }
        return keys_dict



class StreamData(models.Model):

    crawler = models.ForeignKey(Crawler,related_name = 'stream_data',on_delete= models.CASCADE, null=True, blank=True)

    is_running = models.IntegerField(default= 0,help_text = 'Specifies if the stream is running')

    query = models.CharField(max_length=255,blank=True,default='',help_text='List of comma-separated keywords to filter the stream')# comma sepearate list of keywords.
    duration =models.DurationField(help_text= 'Stream will run for the specified duration')
    elapsed = models.DurationField(help_text = 'Elapsed duration of the stream')


    def get_query(self):
        return self.query
