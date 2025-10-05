import eventlet
from celery import Celery
from ...config import BROKER_URL_CELERY, RESULT_BACKEND_CELERY


celery_app = Celery(
    'invisibly',
    broker=BROKER_URL_CELERY,
    backend=RESULT_BACKEND_CELERY,
    include=['service_celery.app.celery.tasks']
)

celery_app.config_from_object('service_celery.app.celery.config') 