from quart import request, jsonify


def register_routes(app, order_processor):

    @app.get("/order-details")
    async def get_order_details():
        order_id = request.args.get("orderId")

        if not order_id:
            return jsonify({"error": "orderId is required"}), 400

        order = order_processor.orders.get(order_id)

        if order is None:
            return jsonify({"error": "Order not found"}), 404

        return jsonify(order), 200
