from collections import defaultdict
from collections import Counter




def contributer_data(tweets):
    #df = pd.DataFrame(tweet_set)
    my_dict = defaultdict(int)


    top_followers = dict()

    top_contributers = None
    unique_contributers = None

    for tweet in tweets:
        my_dict[tweet.user_name] += 1

        top_followers[tweet.user_name] = tweet.user_followers
    # Find_Max = max(my_dict, key=Mydict.get)

    length = len(my_dict)
    if length < 10:
        top_contributers = dict(Counter(my_dict).most_common(length))
        top_followers = dict(Counter(top_followers).most_common(length))
    else:
        top_contributers = dict(Counter(my_dict).most_common(10))
        top_followers = dict(Counter(top_followers).most_common(10))

    unique_contributers = length

    return {'top_contributers':top_contributers,'top_followers': top_followers,'unique_contributers':unique_contributers}