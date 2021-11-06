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

# Checkout item
class CheckoutItem:
    def __init__(self, product, quantity, errors=[]):
        self.product = product
        self.quantity = quantity
        self.errors = []
    
    def add_error(self, error):
        self.errors.append(error)

# Checkout contains the items and total cost and number of items
class Checkout:
    def __init__(self, items, frac_discount, user_id, is_cart=False):
        assert user_id is not None
        # each checkout has a list of products, and a user id
        self.items = items 
        self.user_id = user_id
        self.is_cart = is_cart

        # if a checkout was successful, then it is assigned an order id
        self._order_id = None

        self.subtotal = 0
        self.total_items = 0

        for item in self.items:
            unit_price = item.product['unit_price']
            quantity = item.quantity

            self.subtotal += quantity*unit_price
            self.total_items += quantity
        
        self.discount = self.subtotal * frac_discount
        self.total_cost = self.subtotal * (1-frac_discount)
        self.frac_discount = frac_discount
    
    @property
    def is_valid(self):
        for item in self.items:
            if item.errors:
                return False
        return True
    
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
    
    def get_products(self):
        return self.items

class CheckoutExpired(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# Global checkout database
# Use the sql database to validate checkout sessions
class CheckoutDatabase:
    def __init__(self):
        self.checkouts = {}

    # data = (product_id, quantity)
    def create_checkout(self, cart_items, db, discount, user_id, checkout_id=None, is_cart=False):
        checkout_items = []
        for item in cart_items:
            product_id, quantity = item.product["id"], item.quantity
            product = db.get_entry_by_id("products", product_id)
            if product is None:
                continue
            checkout_items.append(CheckoutItem(product, quantity))
        
        checkout = Checkout(checkout_items, discount, user_id, is_cart=is_cart)
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
        for item in checkout.items:
            id = item.product["id"]
            item.errors = []
            product = db.get_entry_by_id("products", id) 
            if product['is_deleted']:
                item.add_error("Product has been delisted")
    
    def remove_checkout(self, id):
        return self.checkouts.pop(id, None)

    def gen_id(self):
        while True:
            id = str(uuid.uuid4())
            if id not in self.checkouts:
                break
        return id