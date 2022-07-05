import tweepy



def get_rate_limit_status(crawler):

    consumerKey= crawler.consumer_key
    consumerSecret = crawler.consumer_secret
    accessToken= crawler.access_token
    accessSecret= crawler.access_secret

    try:
        auth = tweepy.OAuthHandler(consumerKey,consumerSecret)
        auth.set_access_token(accessToken,accessSecret)
        api = tweepy.API(auth)
    except BaseException as e:
        print("error: get_rate_limit_status()", str(e))

    return api.rate_limit_status()