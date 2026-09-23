import os
import sys
from celery import Celery

# Přidání složky backend do sys.path pro spolehlivý import modulů
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

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
