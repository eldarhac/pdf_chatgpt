import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDIS_URL', 'rediss://:p8b4b378fc0707ac9dc77a56fb80c83c8058bf99217421d5a137f8584d77b70c1@ec2-34-198-204-14.compute-1.amazonaws.com:20110')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
