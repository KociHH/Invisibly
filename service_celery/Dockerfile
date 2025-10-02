FROM python:3.13-slim
LABEL authors="kosini"

WORKDIR /app

RUN pip install --upgrade pip

COPY service_celery/requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt -i https://pypi.org/simple

COPY shared/ /app/shared/
COPY service_celery/ /app/

EXPOSE 8002

CMD ["sh", "-c", "cd app && python main.py"]
