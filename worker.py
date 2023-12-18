import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDIS_URL', 'rediss://:p5a25225b6d26da7c5a06b52c7e1502313124197be3d337fe9c125120c9866acb@ec2-54-211-50-118.compute-1.amazonaws.com:6400')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
