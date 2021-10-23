"""
A temporary in memory database that stores checkout sessions
When a checkout is completed, an order is created for it
When a checkout is abandoned, it remains in memory
"""

import uuid

class CheckoutAlreadyCompleted(Exception):
    def __init__(self, checkout, order_id, **kwargs):
        self.checkout = checkout
        self.order_id = order_id
        message = f"Already assigned order id {order_id}"
        super().__init__(message, **kwargs)

# Checkout contains the items and total cost and number of items
class Checkout:
    def __init__(self, products, user_id):
        # each checkout has a list of products, and a user id
        self.products = products 
        self.user_id = user_id

        # if a checkout was successful, then it is assigned an order id
        self._order_id = None

        self.total_cost = 0
        self.total_items = 0

        for p in self.products:
            unit_price = p['unit_price']
            quantity = p['quantity']

            self.total_cost += quantity*unit_price
            self.total_items += quantity
    
    @property
    def order_id(self):
        return self._order_id
    
    @order_id.setter
    def order_id(self, id):
        if self._order_id is not None:
            raise CheckoutAlreadyCompleted(self, self._order_id)
        self._order_id = id
    
    @property
    def is_completed(self):
        return self.order_id is not None


class CheckoutExpired(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# Global checkout database
# Use the sql database to validate checkout sessions
class CheckoutDatabase:
    def __init__(self):
        self.checkouts = {}

    def create_checkout(self, data, db, user_id, checkout_id=None):
        products = []
        for id, quantity in data:
            product = db.get_entry_by_id("products", id)
            if product is None:
                continue
            products.append({**product, 'quantity': quantity})
        
        checkout = Checkout(products, user_id)
        if checkout_id is None:
            checkout_id = self.gen_id()
        
        self.checkouts[checkout_id] = checkout
        return checkout_id

    # Every checkout needs to be validated against the database 
    def get_checkout(self, id, db):
        checkout = self.checkouts.get(id, None)
        if checkout is None:
            raise KeyError(f"Checkout session doesn't exist")
        self.validate_checkout_from_db(checkout, db)
        return checkout

    def validate_checkout_from_db(self, checkout, db):
        for item in checkout.products:
            id = item["id"]
            product = db.get_entry_by_id("products", id) 
            if product is None:
                raise CheckoutExpired()
    
    def remove_checkout(self, id):
        return self.checkouts.pop(id, None)

    def gen_id(self):
        while True:
            id = str(uuid.uuid4())
            if id not in self.checkouts:
                break
        return id