"""
Api for accessing and modifying a user's cart information
"""
from server import app, get_db
from flask import session
from flask_login import current_user
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

# Cart for logged in users
class DictCart(Cart):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

    
    def to_list(self):
        # for id, quantity in self.items.items():
        #     yield (id, quantity)
        with app.app_context():
            db = get_db()
            cart_items = db.get_entries_by_heading("cart_item", "user_id", self.user_id)
        for cart_item in cart_items:
            id, quantity = cart_item["product_id"], cart_item["quantity"]
            yield (id, quantity)
    # If a previously added product was deleted by the admin, don't show the product in the user's cart
    def purge(self, validator):
        with app.app_context():
            db = get_db()
            cart_items = db.get_entries_by_heading("cart_item", "user_id", self.user_id)
            for cart_item in cart_items:
                product = db.get_entry_by_id("products", cart_item["product_id"])
                if product is None: # If product is non-existend, remove from user cart
                    db.delete_by_id("cart_item", cart_item["id"])
                    print(f"Deleted non-existent product {cart_item['id']} from cart")
    
    # Add product to cart object as well as database
    def add_product(self, product_id, quantity):
        with app.app_context():
            db = get_db()
            cart_item = db.get_entries_by_multiple_headings("cart_item", ("user_id", "product_id"), (self.user_id, product_id)) # should only return 1 or 0 item in list
            print(cart_item)
            if len(cart_item) == 0:
                db.add("cart_item", (product_id, self.user_id, quantity))
            else:
                assert(len(cart_item) == 1)
                cart_item = tuple(x for x in cart_item[0].values()) # Convert dict to tuple of dict values
                db.update("cart_item", cart_item, cart_item)
        # if id not in self.items:
        #     self.items[id] = quantity

        #     return
        # self.items[id] += quantity
    
    def update_product(self, product_id, quantity):
        with app.app_context():
            db = get_db()
            cart_item = db.get_entries_by_multiple_headings("cart_item", ("user_id", "product_id"), (self.user_id, product_id)) # should only return 1 item
            print(cart_item)
        assert(len(cart_item) == 1)
        cart_item = cart_item[0]
        if quantity == 0:
            print("DELETE CART ITEM")
            db.delete_by_id("cart_item", cart_item["id"])
        else:
            print("UPDATE CART ITEM")
            cart_item["quantity"] = quantity
            cart_item = tuple(x for x in cart_item.values()) # Convert dict to tuple of dict values
            # Update quantity amount to non-zero value
            db.update("cart_item", cart_item, cart_item)


        # if id not in self.items and quantity > 0:
        #     self.items[id] = quantity
        #     return
        
        # if id not in self.items:
        #     return
        
        # if quantity > 0:
        #     self.items[id] = quantity
        # else:
        #     del self.items[id]
    
    def empty(self):
        self.items = {}

# convert flask session object to store a cart 
class SessionCart(DictCart):
    def __init__(self, session):
        self.session = session
        self.items = {} 
    
    @property
    def items(self):
        return self.session.setdefault('cart', {})
    
    # def to_list(self):
    #     self.session.
    #     return self.session.setdefault('cart', {})


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
    # cart = SessionCart(session)
    print("GETTING USER CART")
    # TODO: Replace this with the cart in sql database when done
    # if not current_user.is_authenticated:
    #     # create a new cart for not logged in user
    #     cart = SessionCart(session)
    #     print("New cart for unloggedin user")
    # else:
    # Get cart for user
    with app.app_context():
        db = get_db()
        # Get user id
    
    user_id = current_user.get_id()
    cart = DictCart(user_id)
        
        # Get all product items belonging to the user

    cart_items = db.get_entries_by_heading("cart_item", "user_id", user_id)
    for cart_item in cart_items:
        cart.add_product(cart_item['product_id'], cart_item['quantity'])

    # # Get the cart object from database for user
    # cart = db.get_entry_by_id("cart", user_id)
    
    # if cart is None:    # If doesnt exist, create a new one and append to user
    #     db.add("cart", (user_id,))
    # cart = db.get_entries_by_heading("cart", "user_id", user_id)
    print("Retrieving existing cart")
    cart.purge(validate_product_id)
# cart.purge(validate_product_id)
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
