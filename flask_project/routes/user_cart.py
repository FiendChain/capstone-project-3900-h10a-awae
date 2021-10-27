"""
Routes for modifying a user's cart
This includes a logged in user, or an anonymous user
"""

from flask import json, redirect, request, render_template, url_for, jsonify, abort, session

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
        for id, quantity in cart.to_list():
            product = db.get_entry_by_id("products", id)
            data = {**product, 'quantity': quantity}
            products.append(data)

    data = dict(
        products=products, 
        summary=get_cart_summary(cart))

    return render_template('cart.html', **data)

# Add product to cart
@api_bp.route('/transaction/add', methods=['POST'])
def product_add():
    form = UserPurchaseForm(meta=dict(csrf=False))
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 400

    if not validate_product_id(form.id.data):
        form.id.errors.append("Invalid product id")
        return jsonify(serialize_form(form)), 400

    cart = get_user_cart()
    cart.add_product(form.id.data, form.quantity.data)
    print("Adding id " + form.id.data)
    return jsonify(serialize_form(form))

# Update the quantity of a product in the cart
@api_bp.route('/transactions/update', methods=['POST'])
def product_update():
    form = UserPurchaseForm(meta=dict(csrf=False))
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 400
    
    if not validate_product_id(form.id.data):
        form.id.errors.append("Invalid product id")
        return jsonify(serialize_form(form)), 400

    cart = get_user_cart()
    cart.update_product(form.id.data, form.quantity.data)
    summary = get_cart_summary(cart)

    return jsonify(dict(quantity=form.quantity.data, summary=summary))


# Keep cart total count public in jinja template
@app.context_processor
def cart_total_injector():
    cart = get_user_cart()
    summary = get_cart_summary(cart)
    return dict(current_cart=summary)