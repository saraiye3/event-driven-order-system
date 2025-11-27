FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir quart aio-pika

EXPOSE 5001

CMD ["python", "app.py"]