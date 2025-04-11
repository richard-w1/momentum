from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')

app = Celery('website')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# Add periodic task schedule every min
app.conf.beat_schedule = {
    'send-habit-reminders-every-minute': {
        'task': 'website.tasks.send_habit_reminders_task',
        'schedule': crontab(minute='*'),
    },
}