import asyncio
from quart import Quart
import os
from rabbitmq_consumer import RabbitMQConsumer
from order_processor import OrderProcessor
from web_api import register_routes
from db import init_db


app = Quart(__name__)


async def main():
    rabbit_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")

    # Initialize the database
    init_db()

    # Create one shared processor instance
    order_processor = OrderProcessor()

    # Register API routes and pass the shared processor
    register_routes(app, order_processor)

    # Set up RabbitMQ consumer
    consumer = RabbitMQConsumer(
        host=rabbit_host,
        exchange_name="orders-exchange",
        queue_name="orders-queue",
        order_processor=order_processor,
    )

    # Connect to RabbitMQ
    await consumer.connect()

    # background task for the async consumer
    asyncio.create_task(consumer.start_consuming())

    # run the async web server
    await app.run_task(host="0.0.0.0", port=5001)


if __name__ == "__main__":
    asyncio.run(main())
