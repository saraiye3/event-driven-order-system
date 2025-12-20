from db import save_order


class OrderProcessor:
    def __init__(self):
        pass

    def process_order(self, order):
        order_id = order.get("orderId")
        if not order_id:
            print("[!] Received order without orderId; ignoring.")
            return

        self._calculate_shipping(order)

        try:
            inserted = save_order(order)
            if inserted:
                print(f"[*] Saved order to DB with ID: {order_id}")
            else:
                print(f"[!] Order already exists in DB (ignored): {order_id}")
        except Exception as e:
            print(f"[!] Failed to save order {order_id} to DB: {e}")

    @staticmethod
    def _calculate_shipping(order):
        total_amount = order.get("totalAmount", 0)
        shipping_cost = round((float(total_amount) * 0.02), 2)
        order["shippingCost"] = shipping_cost
