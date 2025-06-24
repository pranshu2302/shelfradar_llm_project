from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'llm_project.settings')

app = Celery('llm_project')

# Load settings from Django settings with a 'CELERY_' namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks from all registered Django app configs
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')