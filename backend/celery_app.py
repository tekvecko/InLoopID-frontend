import os
from celery import Celery

broker_url = os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')

celery = Celery(
    'inloopid_tasks',
    broker=broker_url,
    backend=result_backend,
    include=['zk_tasks']
)

celery.conf.update(
    broker_url=broker_url,
    result_backend=result_backend,
    broker_connection_retry_on_startup=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    worker_pool='solo'
)

if __name__ == '__main__':
    celery.start()
