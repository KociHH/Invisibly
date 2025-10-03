FROM python:3.13-slim
LABEL authors="kosini"

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.org/simple

COPY . .
COPY shared/ /app/shared/

EXPOSE 8004

CMD ["sh", "-c", "cd app && uvicorn main:app --host 0.0.0.0 --port 8004"]