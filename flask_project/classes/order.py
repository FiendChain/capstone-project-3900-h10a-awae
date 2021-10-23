import uuid
import datetime

# TODO: Store this information in the database

# TODO: Decide which parts of the payment information should be stored in the database
class Payment:
    def __init__(self, name, number, expiry, cvc):
        self.name = name
        self.number = number
        self.expiry = expiry
        self.cvc = cvc

class Billing:
    def __init__(self, country, address, state, zip_code):
        self.country = country
        self.address = address
        self.state = state
        self.zip_code = zip_code

class Order:
    # product = list of (product_id, quantity) pairs
    def __init__(self, user_id, products, payment, billing):
        self.user_id = user_id
        self.products = products
        self.payment = payment
        self.billing = billing

        self.time_placed = datetime.datetime.now()
        self.delivery_date = datetime.datetime.now()
        self.cancelled = False

        self.total_cost = 0
        self.total_items = 0

        for p in self.products:
            unit_price = p['unit_price']
            quantity = p['quantity']

            self.total_cost += quantity*unit_price
            self.total_items += quantity


class OrderDB:
    def __init__(self):
        self.orders = {}
    
    def get_orders_by_user_id(self, user_id):
        orders = []
        for id, order in self.orders.items():
            if order.user_id == user_id:
                orders.append((id, order)) 
        return orders

    def add_order(self, order, id=None):
        if id is None:
            id = self.gen_id()
        self.orders[id] = order
        return id
    
    def get_order(self, id):
        return self.orders.get(id, None)

    def gen_id(self):
        while True:
            id = str(uuid.uuid4())
            if id not in self.orders:
                break
        return id