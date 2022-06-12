from .. import constants
import requests
from ..views import default_update,default_delete

from apscheduler.events import EVENT_JOB_EXECUTED,EVENT_JOB_ERROR
import json


'''
try using singleton pattern with scheduler.

'''





def my_listener(event):
    if event.exception:
        print('The job crashed :(')
    else:
        #crawl tweets here.
        print('the job succeeded')




def default_update_job():
    f = open("log.txt", "a")
    result = default_update()
    res = json.dumps(result)
    f.write("starting default update job")
    f.write("result :" + str(res))
    f.write("ending default update job")
    f.close()

def default_delete_job():

    print("starting default delete job")
    result = default_delete()
    print(result)


def delete_trends():
    pass
def delete_tweets():
    pass
