FROM python:3.13-slim
LABEL authors="kosini"

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY service_free/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.org/simple

COPY shared/ /app/shared/
COPY service_free/ /app/

CMD ["sh", "-c", "alembic -c app/alembic.ini upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port ${SERVICE_FREE_PORT}"]