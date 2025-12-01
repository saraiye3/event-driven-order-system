import uuid
from datetime import datetime
import random


class OrderGenerator:
    @staticmethod
    def generate_order(order_id, num_of_items):
        """Generate a sample order with given order_id and number of items."""
        items = []
        for i in range(num_of_items):
            item = {
                "itemId": f"ITEM-{i+1:03d}",
                "quantity": random.randint(1, 10),
                "price": round(random.uniform(5, 150), 2)
            }
            items.append(item)

        total_amount = round(sum(item["quantity"] * item["price"] for item in items), 2)

        return {
            "orderId": f"ORD-{order_id}",
            "customerId": f"CUST-{random.randint(10000, 99999)}",
            "orderDate": datetime.utcnow().replace(second=0, microsecond=0).isoformat() + "Z",
            "items": items,
            "totalAmount": total_amount,
            "currency": random.choice(["ILS", "USD", "EUR", "GBP"]),
            "status": random.choice(["new", "confirmed", "delivered", "done"])
        }
