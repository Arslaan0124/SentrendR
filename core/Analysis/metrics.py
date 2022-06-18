from collections import defaultdict
from collections import Counter

import concurrent.futures
import os
def calc_data(tweet_set,start,end):
    source = defaultdict(int)
    data = defaultdict(int)
    foll = defaultdict(int)
    min = 0
    max = 0
    count = 0
    for i in range(start,end):
        source[tweet_set[i].source] += 1
        data['like'] += tweet_set[i].like_count
        data['retweet'] += tweet_set[i].retweet_count
        data['reply'] += tweet_set[i].reply_count
        count += tweet_set[i].user_followers
        if tweet_set[i].user_followers < min:
            min = tweet_set[i].user_followers
        if tweet_set[i].user_followers > max:
            max = tweet_set[i].user_followers

    return source,data,foll,min,max,count

    #print(source)
def get_tweet_info(tweet_set):
    fut=[]
    start = 0
    end = 0
    if(len(tweet_set) < os.cpu_count() * 10):
        perthread = 1
        length = 1
    else:
        perthread = int(len(tweet_set) / os.cpu_count())
        length = os.cpu_count()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for i in range(length):
            start = end
            if length == 1:
                end = len(tweet_set)
            elif i == length - 1:
                end += (len(tweet_set) - end)
            else:
                end += perthread

            fut.append(executor.submit(calc_data, tweet_set,start,end))

    source = defaultdict(int)
    data = defaultdict(int)
    foll = defaultdict(int)

    source = Counter(source)
    data = Counter(data)
    foll = Counter(foll)
    maximum , minimum = 0, 0
    avg = 0
    for i in fut:
        a,b,c,min,max,count = i.result()
        
        source += Counter(a)
        data += Counter(b)
        foll += Counter(c)
        if min < minimum:
            minimum = min
        if max > maximum:
            maximum = max
        avg += count

    source = dict(source)
    data = dict(data)
    foll = dict(foll)
    foll['max_followers'] = maximum
    foll['min_followers'] = minimum
    foll['avg_followers'] = int(avg / len(tweet_set)) 


    data['like'] = data.get("like", 0)
    data['retweet'] = data.get("retweet", 0)
    data['reply'] = data.get("reply", 0)

    return source,data,foll