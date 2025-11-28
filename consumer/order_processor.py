class OrderProcessor:
    def __init__(self):
        self.orders = {}  # key: orderId, value: order dict

    def process_order(self, order):
        """Process and store the order."""
        self._calculate_shipping(order)

        order_id = order.get("orderId")
        if order_id:
            self.orders[order_id] = order
            print(f"[*] Processed and stored order with ID: {order_id}")
        else:
            print("[!] Received order without orderId; ignoring.")

    @staticmethod
    def _calculate_shipping(order):
        total_amount = order.get("totalAmount", 0)
        shipping_cost = round((total_amount * 0.02), 2)
        order["shippingCost"] = shipping_cost
