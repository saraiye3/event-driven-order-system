FROM python:3.10

WORKDIR /app

RUN pip install --no-cache-dir flask pika

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
