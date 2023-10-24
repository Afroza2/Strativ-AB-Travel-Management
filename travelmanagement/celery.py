from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travelmanagement.settings')

app = Celery('travelmanagement')
app.conf.enable_utc = False

app.config_from_object(settings, namespace='CELERY')

app.autodiscover_tasks()



@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")

@app.task
def fetch_and_store_temperatures_task(latitude, longitude, travel_date):
    from apilist.tasks import fetch_and_store_temperatures
    fetch_and_store_temperatures(latitude, longitude, travel_date)

# app.conf.beat_schedule = {
#     # 'add-task-crontab': {
#     #     'task': 'apilist.tasks.add',
#     #     # 'schedule': crontab(minute=2),
#     #     'schedule': crontab(),
#     #     'args': (1, 16),
#     # },
#     # 'print-task-crontab': {
#     #     'task': 'apilist.tasks.fetch_hourly_data_function',
#     #     'schedule': crontab(minute='*/15'),
#     #     'args': "meow"
#     # },
#     'fetch-and-store-temp-data-contrab': {
#         'task': 'apilist.tasks.fetch_and_store_temperatures',
#         'schedule': crontab(),
#         'args': (latitude, longitude, travel_date),
#     }
# }