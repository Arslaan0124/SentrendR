# from core.views import stream_tweet_response as core_stream_tweet_response
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
# import json

# def stream_tweet_response(tweets,stream_data):

#     ret = core_stream_tweet_response(tweets,stream_data)

#     channel_layer = get_channel_layer()
#     message = {
#         'text':str(len(ret)) + 'tweets have been stored.',
#         'stream_obj_id':stream_data['stream_obj_id'],
#         'response_count':stream_data['response_count'],
#         'elapsed':stream_data['elapsed']
#     }
#     async_to_sync(channel_layer.group_send)(stream_data['username'], {"type": "chat_message","message":json.dumps(message)})

# def stream_response(data):
#     #logic here

#     print("DATA RECIVED")
#     pass
    
# def save_stream_object(stream_obj):
#     stream_obj.save()
#     print("Stream obj recived and saved")