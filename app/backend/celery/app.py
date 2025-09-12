import eventlet
from celery import Celery
from app.backend.celery.config import *
from config.env import BROKER_URL_CELERY, RESULT_BACKEND_CELERY


celery_app = Celery(
    'meetbot',
    broker=BROKER_URL_CELERY,
    backend=RESULT_BACKEND_CELERY,
    include=['app.backend.celery.tasks']
)

celery_app.config_from_object('app.backend.celery.config') 