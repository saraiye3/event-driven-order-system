class OrderProcessor:
    def __init__(self):
        self.orders = {}  # key: orderId, value: order dict

    def process_order(self, order):
        """Process and store the order."""

        order_id_raw = order.get("orderId")

        if not order_id_raw:
            print("[!] Received order without orderId; ignoring.")
            return

        if "-" not in order_id_raw:
            print(f"[!] Invalid orderId format: {order_id_raw}; ignoring.")
            return

        order_id = order_id_raw.split("-", 1)[1]

        if not order_id:
            print(f"[!] Empty orderId after split: {order_id_raw}; ignoring.")
            return

        if order_id in self.orders:
            print(f"[!] Duplicate orderId after processing: {order_id}; ignoring.")
            return

        self._calculate_shipping(order)
        self.orders[order_id] = order
        print(f"[*] Processed and stored order with ID: {order_id}")

    @staticmethod
    def _calculate_shipping(order):
        total_amount = order.get("totalAmount", 0)
        shipping_cost = round((total_amount * 0.02), 2)
        order["shippingCost"] = shipping_cost
