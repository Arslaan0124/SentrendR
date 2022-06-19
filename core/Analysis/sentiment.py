from textblob import TextBlob
import re

def clean_text(text):  
    pat1 = r'@[^ ]+'                   
    pat2 = r'https?://[A-Za-z0-9./]+'  
    pat3 = r'\'s'                      
    pat4 = r'\#\w+'                     
    pat5 = r'&amp '                     
    pat6 = r'[^A-Za-z\s]'               
    combined_pat = r'|'.join((pat1,pat2,pat3,pat4,pat5,pat6))
    text = re.sub(combined_pat,"",text).lower()
    return text.strip()
    
def apply_sentiment(data):
    #data['sentiment'] = data['tweet'].apply(lambda x: (TextBlob(x).sentiment.polarity))
    for i in data:
        i['sentiment'] = TextBlob(i['obj'].tweet_text).sentiment
    return data

def get_sentiment_data(tweet_set):

    tops  = {}

    res_dict = {}


    pos_pol_count= pos_sub_count = 0
    neg_pol_count=neg_sub_count = 0
    neu_pol_count = neu_sub_count = 0

    m = [-1]* 9
    top_pos_1 =  tweet_set[0]
    top_pos_2 =  tweet_set[0]
    top_pos_3 = tweet_set[0]
    top_neg_1 =  tweet_set[0]
    top_neg_2 = tweet_set[0]
    top_neg_3 = tweet_set[0]
    top_neu_1 = tweet_set[0]
    top_neu_2 =  tweet_set[0]
    top_neu_3 =  tweet_set[0]
  

    for tweet in tweet_set:
        sentiment = TextBlob(clean_text(tweet.text)).sentiment
        
    
        if sentiment.polarity > 0.4:
            pos_pol_count += 1

            if tweet.like_count >= m[0]:
                top_pos_3 = top_pos_2
                top_pos_2 = top_pos_1
                top_pos_1 = tweet
                m[0] = tweet.like_count

            elif tweet.like_count >= m[1]:
                top_pos_3 = top_pos_2
                top_pos_2 = tweet
                m[1] = tweet.like_count

            elif tweet.like_count >= m[2]:
                top_pos_3 = tweet
                m[2] = tweet.like_count

        elif sentiment.polarity < 0:
            neg_pol_count += 1

            if tweet.like_count >= m[3]:
                top_neg_3 = top_neg_2
                top_neg_2 = top_neg_1
                top_neg_1 = tweet
                m[3] = tweet.like_count
            elif tweet.like_count >= m[4]:
                top_neg_3 = top_neg_2
                top_neg_2 = tweet
                m[4] = tweet.like_count
            elif tweet.like_count >= m[5]:
                top_neg_3 = tweet
                m[5] = tweet.like_count
        else:
            neu_pol_count += 1

            if tweet.like_count >= m[6]:
                top_neu_3 = top_neu_2
                top_neu_2 = top_neu_1
                top_neu_1 = tweet

                m[6] = tweet.like_count

            elif tweet.like_count >= m[7]:
                top_neu_3 = top_neu_2
                top_neu_2 = tweet
                m[7] = tweet.like_count
            elif tweet.like_count >= m[8]:
                top_neu_3 = tweet
                m[8] = tweet.like_count   

        if sentiment.subjectivity > 0.7:
            pos_sub_count += 1
        elif sentiment.subjectivity < 0.3:
            neg_sub_count += 1
        else:
            neu_sub_count += 1

    res_dict['pos_pol_count'] = pos_pol_count
    res_dict['neg_pol_count'] = neg_pol_count
    res_dict['neu_pol_count'] = neu_pol_count
    res_dict['pos_sub_count'] = pos_sub_count
    res_dict['neg_sub_count'] = neg_sub_count
    res_dict['neu_sub_count'] = neu_sub_count


    tops['top_pos_1'] = top_pos_1
    tops['top_pos_2'] = top_pos_2
    tops['top_pos_3'] = top_pos_3
    tops['top_neg_1'] = top_neg_1
    tops['top_neg_2'] = top_neg_2
    tops['top_neg_3'] = top_neg_3
    tops['top_neu_1'] = top_neu_1
    tops['top_neu_2'] = top_neu_2
    tops['top_neu_3'] = top_neu_3

    return res_dict,tops


def cum_sentiment(tweet_set):

    res_dict = {}

    pos_pol_count= pos_sub_count = 0
    neg_pol_count=neg_sub_count = 0
    neu_pol_count = neu_sub_count = 0

    

    for tweet in tweet_set:

        
        sentiment = tweet.sentiment
       
        if sentiment.polarity > 0.7:
            pos_pol_count += 1
        elif sentiment.polarity < 0.3:
            neg_pol_count += 1
        else:
            neu_pol_count += 1

        if sentiment.subjectivity > 0.7:
            pos_sub_count += 1
        elif sentiment.subjectivity < 0.3:
            neg_sub_count += 1
        else:
            neu_sub_count += 1
    
    res_dict['pos_pol_count'] = pos_pol_count
    res_dict['neg_pol_count'] = neg_pol_count
    res_dict['neu_pol_count'] = neu_pol_count
    res_dict['pos_sub_count'] = pos_sub_count
    res_dict['neg_sub_count'] = neg_sub_count
    res_dict['neu_sub_count'] = neu_sub_count

    return res_dict
