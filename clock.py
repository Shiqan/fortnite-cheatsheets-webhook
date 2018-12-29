import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from rq import Queue

from run import gather_posts
from worker import conn

sched = BlockingScheduler()
q = Queue(connection=conn)


@sched.scheduled_job('interval', minutes=1)
def run_gather_posts():
    logging.info('enqueued gather posts')
    q.enqueue(gather_posts)


sched.start()
