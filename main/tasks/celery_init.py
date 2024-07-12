from celery import Celery
from core.db_conf.db_settings import settings


celery = Celery(
    "tasks1",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    include=["main.tasks.tasks1"]
)

celery.conf.event_serializer = 'pickle'
celery.conf.task_serializer = 'pickle'
celery.conf.result_serializer = 'pickle'
celery.conf.accept_content = ['application/json', 'application/x-python-serialize']