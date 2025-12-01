import pika
import json
import time


class RabbitMQPublisher:
    def __init__(self, host, exchange_name):
        self.host = host
        self.exchange_name = exchange_name

        self.connection = None
        self.channel = None

        self._connect()

    def _connect(self):
        """Establish a connection to RabbitMQ and declare the exchange."""
        user = "sarai"
        password = "carrot"
        port = 5672

        credentials = pika.PlainCredentials(user, password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=port,
            credentials=credentials
        )

        while True:
            try:
                print("[Producer] Trying to connect to RabbitMQ...")

                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()

                # declare exchange once connected
                self.channel.exchange_declare(
                    exchange=self.exchange_name,
                    exchange_type="direct",
                    durable=True
                )

                print("[Producer] Connected and declared exchange.")
                break  # success

            except pika.exceptions.AMQPConnectionError as e:
                print(f"[Producer] RabbitMQ not ready yet, retrying in 2 seconds... ({e})")
                time.sleep(2)

    def publish(self, message: dict):
        """Publish a message to the RabbitMQ exchange."""
        body = json.dumps(message)  # Convert the message dictionary to a JSON string
        routing_key = message.get("status", "unknown")

        try:  # added this part because after a while when no requests are sent the connection dies
            # first attempt
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=routing_key,
                body=body
            )
        except pika.exceptions.StreamLostError:
            # Connection died (RabbitMQ closed it), reconnect
            print("Connection lost. Reconnecting to RabbitMQ...")
            self._connect()

            # second attempt after reconnecting
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=routing_key,
                body=body
            )

    def close(self):
        self.connection.close()
