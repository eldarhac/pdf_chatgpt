import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

redis_url = os.getenv('REDIS_URL', 'rediss://:p661f2835f08b5a51b4c6f9fd13caa598272d3e9c83ab60438531929cee2753e4@ec2-44-214-199-53.compute-1.amazonaws.com:24419')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
