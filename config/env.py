from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

def load_from_env(name: str, env_path: str = ".env") -> str | None:
    load_dotenv(env_path)
    exenv = os.getenv(name)
    if not exenv:
        logger.warning(f'Не найдено значение {name} в env файле [{env_path}]')
    return exenv

l = load_from_env

NAME_PROJECT = l("NAME_PROJECT")
POSTGRES_URL = l("POSTGRES_URL")

UPORT = int(l("UPORT"))
UHOST = l("UHOST")

SECRET_KEY = l("SECRET_KEY")
SECRET_KEY_SIZE = int(l("SECRET_KEY_SIZE"))
TOKEN_LIFETIME_DAYS = int(l("TOKEN_LIFETIME_DAYS"))

ACCESS_TOKEN_LIFETIME_MINUTES = int(l("ACCESS_TOKEN_LIFETIME_MINUTES"))
REFRESH_TOKEN_LIFETIME_DAYS = int(l("REFRESH_TOKEN_LIFETIME_DAYS"))

BROKER_URL_CELERY = l("BROKER_URL_CELERY")
RESULT_BACKEND_CELERY = l("RESULT_BACKEND_CELERY")

ADMIN_CONFIRMATION_IP = l("ADMIN_CONFIRMATION_IP")

SMTP_HOST = l("SMTP_HOST")
SMTP_PORT = l("SMTP_PORT")
SMTP_EMAIL = l("SMTP_EMAIL")
SMTP_PASS = l("SMTP_PASS")