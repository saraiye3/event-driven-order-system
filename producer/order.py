class Order:
    def __init__(self, order_id, customer_id, order_date, items, total_amount, currency, status):
        self.order_id = order_id
        self.customer_id = customer_id
        self.order_date = order_date
        self.items = items  # List of OrderItem objects
        self.total_amount = total_amount
        self.currency = currency
        self.status = status
