from flask import request, jsonify
from order_validator import OrderValidator
from order_generator import OrderGenerator


def register_routes(app, publisher):

    # Seen order IDs for duplicate validation
    seen_order_ids = set()
    
    @app.route("/create-order", methods=["POST"])
    def create_new_order():
        data = request.get_json()  # Converts incoming JSON to a Python dictionary

        order_id = data.get("orderId")
        num_of_items = data.get("numberOfItems")

        error = OrderValidator.validate_input(order_id, num_of_items)
        if error is not None:
            return jsonify({"error": error}), 400

        if order_id in seen_order_ids:
            return jsonify({"error": "orderId already exists"}), 409

        # Generate order
        order = OrderGenerator.generate_order(order_id, num_of_items)

        # Publish to RabbitMQ
        try:
            publisher.publish(order)
        except Exception as e:
            return jsonify({"error": f"Failed to publish order: {str(e)}"}), 500

        return jsonify(order), 201
