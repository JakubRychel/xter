import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xter.settings')

app = Celery('xter')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update-median-metrics-every-hour': {
        'task': 'posts.tasks.set_recommendation_params',
        'schedule': crontab(minute=0, hour='*'),
    },
}