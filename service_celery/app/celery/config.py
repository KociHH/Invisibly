task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'Europe/Moscow'
enable_utc = True

# celery -A service_celery.app.celery.app worker -l info -P solo
# celery -A service_celery.app.celery.app beat -l info

worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 1000
worker_max_memory_per_child = 150000

path_tasks = 'service_celery.app.celery.tasks.'
beat_schedule = {
    'check-jwt-token-date': {
        'task': path_tasks + 'check_jwt_token_date',
        'schedule': 86400,
    },
    'cleaning-expiring-json': {
        'task': path_tasks + 'cleaning_expiring_json',
        'shedule': 350,
    }
}
