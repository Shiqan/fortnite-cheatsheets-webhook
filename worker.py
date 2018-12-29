import logging
import os

import redis
from rq import Connection, Queue, Worker

log = logging.getLogger()
log.setLevel(os.getenv('LOG_LEVEL', 'DEBUG'))

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    log.info('Started worker.py')
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
