from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import tweepy



def validate_api_keys(consumer_key,consumer_secret,access_token,access_token_secret):

    auth = tweepy.OAuth1UserHandler(consumer_key,consumer_secret,access_token, access_token_secret)
    api = tweepy.API(auth)
    try:
        api.verify_credentials()
        return True
    except:
        return False

def validate_bearer_token(bearer_token):
    pass

        


