class OrderValidator:
    @staticmethod
    def validate_input(order_id, num_of_items):
        if order_id is None or str(order_id).strip() == "":
            return "orderId is required"

        if num_of_items <= 0:
            return "number of items must be greater than zero"

        return None
