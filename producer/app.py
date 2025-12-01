from flask import Flask
import os
from web_api import register_routes
from rabbitmq_publisher import RabbitMQPublisher


def create_publisher():
    return RabbitMQPublisher(
        host=os.environ.get("RABBITMQ_HOST", "rabbitmq"),
        exchange_name="orders-exchange"
    )


def create_app():
    app = Flask(__name__)
    pub = create_publisher()

    register_routes(app, pub)

    return app, pub


app, publisher = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
