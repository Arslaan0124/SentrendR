from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED,EVENT_JOB_ERROR
import datetime


from . import jobs
def start():

    scheduler = BackgroundScheduler()

    default_update_job = scheduler.add_job(jobs.default_update_job, 'interval', hours = 7)

    
    default_delete_job = scheduler.add_job(jobs.default_delete_job, 'interval', hours = 7)

    scheduler.add_listener(jobs.my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    scheduler.start()

def initial_job():
    now = datetime.datetime.now()
    now_plus_1 = now + datetime.timedelta(minutes = 1)
    initscheduler = BackgroundScheduler()
    initscheduler.add_job(jobs.default_update_job,'date', run_date=now_plus_1)
    initscheduler.start()
    print("INITIAL JOB CALLED")
