from quart import request, jsonify
from db import get_order


def register_routes(app, order_processor):

    @app.get("/order-details")
    async def get_order_details():
        order_id = request.args.get("orderId")

        if not order_id:
            return jsonify({"error": "orderId is required"}), 400

        order = get_order(order_id)

        if order is None:
            return jsonify({"error": "Order not found"}), 404

        return jsonify(order), 200
