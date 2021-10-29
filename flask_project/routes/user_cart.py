"""
Routes for modifying a user's cart
This includes a logged in user, or an anonymous user
"""

from flask import json, redirect, request, render_template, url_for, jsonify, abort, session
from flask_login import current_user

from server import  app, get_db
from .forms import UserPurchaseForm, serialize_form

from .endpoints import user_bp, api_bp
from .cart import get_user_cart, get_cart_summary, validate_product_id

# Render the cart page
@user_bp.route('/cart', methods=['GET'])
def cart():
    cart = get_user_cart()
    products = []

    with app.app_context():
        db = get_db()
        for cart_item in cart.to_list():
            product = db.get_entry_by_id("products", cart_item["product_id"])
            data = {**product, 'quantity': cart_item["quantity"]}
            products.append(data)

    data = dict(
        products=products, 
        summary=get_cart_summary(cart))

    return render_template('cart.html', **data)

# Add product to cart from product page when user clicks "Add to cart"
@api_bp.route('/transaction/add', methods=['POST'])
def product_add():
    print("ADDING PRODUCT")
    form = UserPurchaseForm(meta=dict(csrf=False))
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 400

    if not validate_product_id(form.id.data):
        form.id.errors.append("Invalid product id")
        return jsonify(serialize_form(form)), 400

    with app.app_context():
        db = get_db()
    
    # Check if db has enough stock for requested quantity
    product = db.get_entry_by_id("products", form.id.data)
    if form.quantity.data > product["stock"]:
        print("Database does not have enough stock")
        return jsonify(serialize_form(form)), 400

    cart_item = db.get_entries_by_multiple_headings("cart_item", ("product_id", "user_id"), (form.id.data, current_user.get_id()))
    # print(cart_item)
    # If item already exists in cart, update with new quantity
    if cart_item != []:
        assert(len(cart_item) == 1)
        cart_item = cart_item[0]
        cart_item["quantity"] += form.quantity.data
        cart_item = tuple(v for v in cart_item.values())
        db.update("cart_item", cart_item, cart_item)\
    
    # If item not in cart, add new entry to cart
    else:
        cart_item = (form.id.data, current_user.get_id(), form.quantity.data)
        db.add("cart_item", cart_item)
    
    # Update database quantity
    product["stock"] -= form.quantity.data
    product = tuple(v for v in product.values())
    db.update("products", product, product)
    print(f"Added product id {form.id.data}")
    return jsonify(serialize_form(form))

# Update the quantity of a product in the cart on cart page
@api_bp.route('/transactions/update', methods=['POST'])
def product_update():
    print("UPATING PRODUCT")
    form = UserPurchaseForm(meta=dict(csrf=False))
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 400
    
    if not validate_product_id(form.id.data):
        form.id.errors.append("Invalid product id")
        return jsonify(serialize_form(form)), 400

    cart = get_user_cart()
    with app.app_context():
        db = get_db()
    product = db.get_entry_by_id("products", form.id.data)

    # Check if requested user quantity is <= database amount
    if form.quantity.data > product["stock"]:
        print("Database does not have enough stock")
        return jsonify(serialize_form(form)), 400
    
    # Update cart with new quantity
    cart_item = db.get_entries_by_multiple_headings("cart_item", ("product_id", "user_id"), (form.id.data, current_user.get_id()))
    assert(len(cart_item) == 1)
    cart_item = cart_item[0]
    quantity_old = cart_item["quantity"]
    quantity_new = form.quantity.data
    cart_item["quantity"] = quantity_new
    cart_item = tuple(v for v in cart_item.values())
    db.update("cart_item", cart_item, cart_item)

    # Update db with new quantity
    product["stock"] += quantity_old - quantity_new
    product = tuple(v for v in product.values())
    db.update("products", product, product)
    summary = get_cart_summary(cart)

    return jsonify(dict(quantity=form.quantity.data, summary=summary))


# Keep cart total count public in jinja template
@app.context_processor
def cart_total_injector():
    cart = get_user_cart()
    summary = get_cart_summary(cart)
    return dict(current_cart=summary)


def update_db_stock(product, quantity_delta, db):
    product["stock"] += quantity_delta
    print(f"Updating cart item by quantity {quantity_delta}")
    product = tuple(v for v in product.values())
    db.update("products", product, product)