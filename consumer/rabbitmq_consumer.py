import asyncio
import json
import aio_pika
import os


class RabbitMQConsumer:
    def __init__(self, host, exchange_name, queue_name, order_processor):
        self.host = host
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.order_processor = order_processor

        self.connection = None
        self.channel = None
        self.queue = None

    async def connect(self):
        """Connect to RabbitMQ, declare queue, and bind it to existing exchange with routing key 'new'."""
        user = os.environ.get("RABBITMQ_USER", "sarai")
        password = os.environ.get("RABBITMQ_PASS", "carrot")
        port = 5672

        # Keep retrying until RabbitMQ becomes available
        while True:
            try:
                print("[*] Attempting to connect to RabbitMQ...")

                self.connection = await aio_pika.connect_robust(
                    host=self.host,
                    port=port,
                    login=user,
                    password=password,
                    heartbeat=30
                )
                break  # Connection succeeded, exit retry loop

            except Exception as e:
                print(f"[!] Connection failed: {e}. Retrying in 2 seconds...")
                await asyncio.sleep(2)  # Wait before retrying

        # Open a channel after connection is established
        self.channel = await self.connection.channel()

        # Declare the queue
        self.queue = await self.channel.declare_queue(
            self.queue_name,
            durable=True
        )

        # Bind queue to an existing exchange by name, using routing key "order.new.#"
        await self.queue.bind(self.exchange_name, routing_key="order.new.#")

        print(
            f"[*] Connected to RabbitMQ, bound to exchange "
            f"'{self.exchange_name}' with routing key 'new'."
        )

    async def start_consuming(self):
        """Start consuming messages asynchronously and process orders."""
        if self.queue is None:
            raise RuntimeError("You must call connect() before start_consuming().")

        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():  # auto-ack if succeeds or nack if exception
                    body = message.body.decode("utf-8")
                    print(f"[x] Received raw message: {body}")

                    try:
                        order = json.loads(body)
                    except json.JSONDecodeError:
                        print("[!] Invalid JSON, skipping")
                        continue

                    try:
                        self.order_processor.process_order(order)
                    except Exception as e:
                        print(f"[!] Error processing order: {e}")
                        continue
