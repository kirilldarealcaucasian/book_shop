from celery import Celery
from celery.schedules import crontab

from core.config import settings


celery = Celery(
    "tasks1",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    include=["application.tasks.tasks1"],
)

celery.conf.beat_schedule = {
    'save-logs-every-minute': {
        'task': 'application.tasks.tasks1.save_log',
        'schedule': crontab(minute='*/1'),  # run every minute
        'args': (),
    },
}

celery.conf.event_serializer = 'pickle'
celery.conf.task_serializer = 'pickle'
celery.conf.result_serializer = 'pickle'
celery.conf.accept_content = ['application/json', 'application/x-python-serialize']

