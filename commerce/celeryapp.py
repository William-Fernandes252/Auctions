from __future__ import absolute_import
from os import environ
from celery import Celery
from django.conf import settings


environ.setdefault('DJANGO_SETTINGS_MODULE', 'commerce.settings')
app = Celery('commerce.celery')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))