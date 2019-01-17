import os
import time

from apscheduler.schedulers.blocking import BlockingScheduler

from run import gather_posts

day_of_week = os.getenv('SCHEDULE_DAY_OF_WEEK', 'thu')
hour = os.getenv('SCHEDULE_HOUR', '15-24')

if __name__ == '__main__':
    sched = BlockingScheduler()
    sched.add_job(gather_posts, 'cron', id='gather_posts', day_of_week=day_of_week, hour=hour)
    sched.start()
