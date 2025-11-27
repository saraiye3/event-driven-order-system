import asyncio
import json
import aio_pika
from quart import Quart, request, jsonify
import os

# ============================
# Global in-memory store
# ============================

orders = {}  # key: orderId, value: order dict


# ============================
# Async RabbitMQ Consumer
# ============================

class RabbitMQConsumer:
    def __init__(self, host, exchange_name, queue_name):
        self.host = host
        self.exchange_name = exchange_name  # just the name as string
        self.queue_name = queue_name

        self.connection = None
        self.channel = None
        self.queue = None

    async def connect(self):
        """Connect to RabbitMQ, declare queue, and bind it to existing exchange with routing key 'new'."""
        user = "sarai"
        password = "carrot"
        port = 5672

        # Retry connection a few times until RabbitMQ is ready
        for attempt in range(1, 6):  # 5 attempts
            try:
                print(f"[*] Connecting to RabbitMQ (attempt {attempt})...")

                self.connection = await aio_pika.connect_robust(
                    host=self.host,
                    port=port,
                    login=user,
                    password=password,
                )
                break  # success, exit the loop

            except Exception as e:
                print(f"[!] Connection failed: {e}")
                if attempt == 5:
                    raise  # give up after final attempt
                await asyncio.sleep(2)  # wait before retrying

        self.channel = await self.connection.channel()

        # Declare the queue
        self.queue = await self.channel.declare_queue(
            self.queue_name,
            durable=True,
        )

        # Bind queue to an existing exchange by name, using routing key "new"
        await self.queue.bind(self.exchange_name, routing_key="new")

        print("[*] Connected to RabbitMQ, bound to exchange "
              f"'{self.exchange_name}' with routing key 'new'.")

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

                    total_amount = order.get("totalAmount", 0)
                    shipping_cost = round((total_amount * 0.02), 2)
                    order["shippingCost"] = shipping_cost

                    order_id = order.get("orderId")
                    if order_id:
                        orders[order_id] = order
                        print(f"[+] Order processed and saved: {order}")
                    else:
                        print("[!] Missing orderId, order not saved")


# ============================
# Async API (Quart)
# ============================

app = Quart(__name__)


@app.get("/order-details")
async def get_order_details():
    """Return stored order details by orderId."""
    order_id = request.args.get("orderId")

    if not order_id:
        return jsonify({"error": "orderId is required"}), 400

    order = orders.get(order_id)

    if order is None:
        return jsonify({"error": "Order not found"}), 404

    return jsonify(order), 200


# ============================
# Main: Start Consumer + API
# ============================

async def main():
    rabbit_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")

    consumer = RabbitMQConsumer(
        host=rabbit_host,
        exchange_name="orders-exchange",
        queue_name="orders-queue",
    )

    await consumer.connect()

    # background task for the async consumer
    asyncio.create_task(consumer.start_consuming())

    # run the async web server
    await app.run_task(host="0.0.0.0", port=5001)


if __name__ == "__main__":
    asyncio.run(main())
