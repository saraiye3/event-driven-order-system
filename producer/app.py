from flask import Flask, request, jsonify
from order_validator import OrderValidator
from order_generator import OrderGenerator
from rabbitmq_publisher import RabbitMQPublisher
import os

app = Flask(__name__)

publisher = RabbitMQPublisher(
    host=os.environ.get("RABBITMQ_HOST", "rabbitmq"),
    exchange_name="orders-exchange",
)

@app.route("/create-order", methods=["POST"])
def create_new_order():
    """Endpoint to create and publish an order."""
    data = request.get_json()

    order_id = data.get("orderId")
    num_of_items = data.get("numberOfItems")

    error = OrderValidator.validate_input(order_id, num_of_items)
    if error is not None:
        return jsonify({"error": error}), 400

    """Generate order data."""
    order = OrderGenerator.generate_order(order_id, num_of_items)

    """Publish order to RabbitMQ."""
    publisher.publish(order)

    return jsonify(order), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
