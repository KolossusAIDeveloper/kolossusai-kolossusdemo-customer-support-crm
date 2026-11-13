from celery import Celery
from app.config import settings

celery_app = Celery(
    "crm_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "check-overdue-tasks": {
            "task": "app.tasks.check_overdue_tasks",
            "schedule": 3600.0,
        },
    },
)
