from flask import request, jsonify
from order_validator import OrderValidator
from order_generator import OrderGenerator


def register_routes(app, publisher):

    @app.route("/create-order", methods=["POST"])
    def create_new_order():
        data = request.get_json()

        order_id = data.get("orderId")
        num_of_items = data.get("numberOfItems")

        error = OrderValidator.validate_input(order_id, num_of_items)
        if error is not None:
            return jsonify({"error": error}), 400

        # Generate order
        order = OrderGenerator.generate_order(order_id, num_of_items)

        # Publish to RabbitMQ
        publisher.publish(order)

        return jsonify(order), 201
