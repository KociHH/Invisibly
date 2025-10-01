import eventlet
from celery import Celery
from config.env import BROKER_URL_CELERY, RESULT_BACKEND_CELERY


celery_app = Celery(
    'meetbot',
    broker=BROKER_URL_CELERY,
    backend=RESULT_BACKEND_CELERY,
    include=['service_celery.app.celery.tasks']
)

celery_app.config_from_object('service_celery.app.celery.config') 