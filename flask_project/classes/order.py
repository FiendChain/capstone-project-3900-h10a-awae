import uuid
import datetime

from server import app, get_db

class OrderItem:
    def __init__(self, product, quantity, price):
        self.product = product
        self.quantity = quantity
        self.price = price

class Order:
    # product = list of (product_id, quantity) pairs
    def __init__(self, order_id):
        self.id = order_id

        with app.app_context():
            db = get_db()

        # get order from database 
        order_db = db.get_entry_by_id("order2", order_id)
        if order_db is None:
            raise KeyError(f'Invalid order id={order_id}')

        # get payment info
        self.payment = db.get_entry_by_id("payment_past", order_db["payment_past_id"])
        self.billing = db.get_entry_by_id("billing_past", order_db["billing_past_id"])

        # get order items
        order_items_db = db.get_entries_by_heading("order2_item", "order2_id", order_db["id"])
        self.items = []
        for item_db in order_items_db:
            product = db.get_entry_by_id("products", item_db["product_id"]) 
            quantity = item_db['quantity']
            price = item_db['price']
            self.items.append(OrderItem(product, quantity, price))

        self.user_id = order_db['user_id']

        self.time_placed = datetime.datetime.now()

        # get summary of order
        self.subtotal = order_db['subtotal']
        self.discount = order_db['discount']
        self.total_cost = order_db['total_cost']
        self.total_items = order_db['total_items']