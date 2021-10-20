"""
Api for accessing and modifying a user's cart information
"""
from server import app, get_db
from flask import session

from abc import ABC, abstractmethod
# rough outline of how cart data is stored
class Cart(ABC):
    @abstractmethod
    def to_list(self):
        pass

    @abstractmethod
    def purge(self, validator):
        pass

    @abstractmethod
    def add_product(self, id, quantity):
        pass

    @abstractmethod
    def update_product(self, id, quantity):
        pass

    @abstractmethod
    def empty(self):
        pass

class DictCart(Cart):
    def __init__(self):
        super().__init__()
        self.items = {} 
    
    def to_list(self):
        for id, quantity in self.items.items():
            yield (id, quantity)
    
    def purge(self, validator):
        bad_ids = [id for id in self.items if not validator(id)]
        for id in bad_ids:
            del self.items[id]
    
    def add_product(self, id, quantity):
        if id not in self.items:
            self.items[id] = quantity
            return
        self.items[id] += quantity
    
    def update_product(self, id, quantity):
        if id not in self.items and quantity > 0:
            self.items[id] = quantity
            return
        
        if id not in self.items:
            return
        
        if quantity > 0:
            self.items[id] = quantity
        else:
            del self.items[id]
    
    def empty(self):
        self.items = {}

# convert flask session object to store a cart 
class SessionCart(DictCart):
    def __init__(self, session):
        self.session = session
    
    @property
    def items(self):
        return self.session.setdefault('cart', {})
    
    def add_product(self, id, quantity):
        rv = super().add_product(id, quantity)
        self.session.modified = True
        print(f'Added: {self.session}')
        return rv
    
    def update_product(self, id, quantity):
        rv = super().update_product(id, quantity)
        self.session.modified = True
        print(f'Updated: {self.session}')
        return rv
    
    def empty(self):
        self.session['cart'] = {}
        self.session.modified = True

# Cart and purchasing
def validate_product_id(id):
    with app.app_context():
        db = get_db()
        product = db.get_entry_by_id("products", id)
    
    if product:
        return True
    return False

# Depending on whether a user is logged in, we can store cart in flask-session or mock db
def get_user_cart():
    cart = SessionCart(session)

    # TODO: Replace this with the cart in sql database when done
    # if not current_user.is_authenticated:
    #     cart = SessionCart(session)
    # else:
    #     cart = current_user.cart

    cart.purge(validate_product_id)
    return cart

# Get a dict containing summary information about a cart
def get_cart_summary(cart):
    total_items = 0
    total_cost = 0
    with app.app_context():
        db = get_db()
        for id, quantity in cart.to_list():
            product = db.get_entry_by_id("products", id)
            total_items += quantity
            total_cost += quantity*product['unit_price']
    return {"total_items": total_items, "total_cost": total_cost}
