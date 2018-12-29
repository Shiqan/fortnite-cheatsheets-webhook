import os
import time 

from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue

from run import gather_posts
from worker import conn

sched = BlockingScheduler()
q = Queue(connection=conn)

interval = int(os.getenv('SCHEDULE_INTERVAL', 30))


@sched.scheduled_job('interval', minutes=interval)
def run_gather_posts():
    q.enqueue(gather_posts)


sched.start()
