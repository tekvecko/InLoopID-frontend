import os
import sys
from celery import Celery

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

broker_url = os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://127.0.0.1:6379/0')
task_default_queue = os.getenv('CELERY_TASK_DEFAULT_QUEUE', 'celery')

celery = Celery(
    'inloopid_tasks',
    broker=broker_url,
    backend=result_backend,
    include=[
        'zk_tasks',
        'hr_tasks',
        'anchor_tasks',
        'tasks',
    ]
)

celery.conf.update(
    broker_url=broker_url,
    result_backend=result_backend,
    broker_connection_retry_on_startup=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    task_default_queue=task_default_queue,
    worker_pool='solo'
)

if __name__ == '__main__':
    celery.start()

# ===== INLOOPID_OUTBOX_BEAT_V1 =====
_existing_imports = list(
    celery.conf.imports or ()
)

if "outbox_tasks" not in _existing_imports:
    _existing_imports.append(
        "outbox_tasks"
    )

celery.conf.imports = tuple(
    _existing_imports
)

_beat = dict(
    celery.conf.beat_schedule or {}
)

_beat["inloopid-outbox-dispatch"] = {
    "task": "outbox.dispatch",
    "schedule": 5.0,
    "options": {
        "queue": os.getenv(
            "CELERY_TASK_DEFAULT_QUEUE",
            "celery",
        ),
    },
}

celery.conf.beat_schedule = _beat
# ===== /INLOOPID_OUTBOX_BEAT_V1 =====
