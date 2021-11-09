"""
Api for accessing and modifying a user's cart information
"""

from server import app, get_db
from flask import session
from flask_login import current_user

class InvalidProduct(Exception):
    def __init__(self, product_id):
        self.product_id = product_id
        super().__init__(f"Invalid product id ({product_id})")

class OutOfStock(Exception):
    def __init__(self, product_id, available_stock, target_stock):
        self.available_stock = available_stock
        self.target_stock = target_stock
        self.product_id = product_id
        super().__init__(f"Insufficient stock for product {product_id}")

# Cart for logged in users
class Cart:
    def __init__(self, user_id):
        self.user_id = user_id

    @property 
    def db_items(self):
        with app.app_context():
            db = get_db()
        cart_items = db.get_entries_by_heading("cart_item", "user_id", self.user_id)
        return cart_items

    # construct the full cart item with product data 
    @property
    def items(self):
        with app.app_context():
            db = get_db()
        cart_items = db.get_entries_by_heading("cart_item", "user_id", self.user_id)

        products = []
        for cart_item in cart_items:
            product = db.get_entry_by_id("products", cart_item["product_id"])
            products.append({**product, 'quantity': cart_item['quantity']}) 

        return products

    # If a previously added product was deleted by the admin, don't show the product in the user's cart
    # TODO: Add a warning to the cart if there is a deleted product
    def purge(self):
        with app.app_context():
            db = get_db()

        cart_items = db.get_entries_by_heading("cart_item", "user_id", self.user_id)
        for cart_item in cart_items:
            product = db.get_entry_by_id("products", cart_item["product_id"])
            if product is None: 
                db.delete_by_id("cart_item", cart_item["id"])
    
    # Add product to cart object
    def add_product(self, product_id, quantity):
        assert quantity > 0

        with app.app_context():
            db = get_db()
        
        product = db.get_entry_by_id("products", product_id)
        if not product:
            raise InvalidProduct(product_id)
        
        if quantity > product["stock"]:
            raise OutOfStock(product_id, product["stock"], quantity)
        
        cart_item = db.get_entries_by_multiple_headings(
            "cart_item", 
            ("product_id", "user_id"), 
            (product_id, self.user_id))
        
        cart_item = cart_item[0] if cart_item else None

        # create cart entry 
        if not cart_item:
            cart_item = (product_id, self.user_id, quantity)
            db.add("cart_item", cart_item)
        # update cart entry
        else:
            cart_item_old = list(cart_item.values())
            cart_item['quantity'] += quantity
            cart_item_new = list(cart_item.values())
            db.update("cart_item", cart_item_old, cart_item_new)
        
        # update stock
        product_old = list(product.values())
        product['stock'] -= quantity
        product_new = list(product.values())
        db.update("products", product_old, product_new)
    
    # Change cart quantity to new quantity
    # returns the final quantity that was possible to achieve
    def update_product(self, product_id, quantity):
        assert quantity >= 0

        with app.app_context():
            db = get_db()
        
        product = db.get_entry_by_id("products", product_id)
        if not product:
            raise InvalidProduct(product_id)
        
        cart_item = db.get_entries_by_multiple_headings(
            "cart_item", 
            ("product_id", "user_id"), 
            (product_id, self.user_id))
        
        cart_item = cart_item[0] if cart_item else None


        # create cart item with maximum possible stock
        if not cart_item:
            final_quantity = min(quantity, product['stock'])
            stock_diff = final_quantity
            if final_quantity > 0:
                cart_item = (product_id, self.user_id, final_quantity)
                db.add("cart_item", cart_item)
        # update cart entry
        else:
            cart_item_old = list(cart_item.values())

            original_quantity = cart_item['quantity']
            stock_diff = quantity-original_quantity
            stock_diff = min(stock_diff, product['stock'])
            final_quantity = stock_diff+original_quantity
            cart_item['quantity'] = final_quantity

            cart_item_new = list(cart_item.values())

            if final_quantity > 0:
                db.update("cart_item", cart_item_old, cart_item_new)
            else:
                db.delete("cart_item", cart_item_old)
        
        # update stock
        product_old = list(product.values())
        product['stock'] -= stock_diff
        product_new = list(product.values())
        db.update("products", product_old, product_new)
    
        return final_quantity
    
    def empty(self):
        with app.app_context():
            db = get_db()
        cart_items = db.get_entries_by_heading("cart_item", "user_id", self.user_id)
        for cart_item in cart_items:
            db.delete_by_id("cart_item", cart_item["id"])

# Depending on whether a user is logged in, we can store cart in flask-session or mock db
def get_user_cart():
    user_id = current_user.get_id()
    cart = Cart(user_id)
    cart.purge()

    return cart

# Get a dict containing summary information about a cart
def get_cart_summary(cart):
    total_items = 0
    total_cost = 0

    for cart_item in cart.items:
        total_items += cart_item["quantity"]
        total_cost += cart_item["quantity"]*cart_item['unit_price']
    return {"total_items": total_items, "total_cost": total_cost}
