FROM python:3.13-slim
LABEL authors="kosini"

WORKDIR /app

RUN pip install --upgrade pip

COPY service_chat/requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt -i https://pypi.org/simple

COPY shared/ /app/shared/
COPY service_chat/ /app/

CMD ["sh", "-c", "alembic -c app/alembic.ini upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${SERVICE_CHAT_PORT}"]