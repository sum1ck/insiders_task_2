# celery_app.py for Celery setup 
from celery import Celery
from core.config import settings

celery_app = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["tasks.service"]
)

celery_app.conf.beat_schedule = {
    "mark-overdue-tasks-every-5-minutes": {
        "task": "tasks.service.mark_overdue_tasks",
        "schedule": 300,
    },
} 