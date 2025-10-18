"""
RQ worker entrypoint. Run this with:

    rq worker high default

Assumes Redis is running on localhost:6379 and this repo is in PYTHONPATH.
"""
from redis import Redis
from rq import Queue, Worker, Connection
import os

redis_conn = Redis(host=os.environ.get('REDIS_HOST','localhost'), port=int(os.environ.get('REDIS_PORT','6379')))
q = Queue('default', connection=redis_conn)

if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(['default'])
        worker.work()
