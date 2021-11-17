"""
Routes for modifying a user's cart
This includes a logged in user, or an anonymous user
"""

from flask import json, redirect, request, render_template, url_for, jsonify, abort, session
from flask.helpers import flash
from flask_login import current_user

from server import  app
from .forms import UserPurchaseForm, serialize_form

from .endpoints import user_bp, api_bp
from classes.cart import InvalidProduct, OutOfStock, DelistedProduct, get_user_cart, get_cart_summary

# Render the cart page
@user_bp.route('/cart', methods=['GET'])
def cart():
    cart = get_user_cart()
    data = dict(
        products=cart.items, 
        summary=get_cart_summary(cart))

    return render_template('cart.html', **data)

# Send cart as json 
@api_bp.route("/cart", methods=['GET'])
def cart_data():
    cart = get_user_cart()
    cart_items = cart.items
    cart_items = [item.to_json() for item in cart_items]
    return jsonify(dict(cart_items=cart_items)), 200

# Add product to cart from product page when user clicks "Add to cart"
@api_bp.route('/transaction/add', methods=['POST'])
def product_add():
    form = UserPurchaseForm(meta=dict(csrf=False))

    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 400

    cart = get_user_cart() 

    try:
        cart.add_product(form.id.data, form.quantity.data)
    except InvalidProduct:
        return jsonify(serialize_form(form)), 400
    except OutOfStock:
        return jsonify(serialize_form(form)), 400
    except DelistedProduct:
        return jsonify(dict(error="Delisted product")), 400

    return jsonify(serialize_form(form)), 200

# Update the quantity of a product in the cart on cart page
@api_bp.route('/transaction/update', methods=['POST'])
def product_update():
    form = UserPurchaseForm(meta=dict(csrf=False))

    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 400
    
    cart = get_user_cart()
    try:
        final_quantity = cart.update_product(form.id.data, form.quantity.data)
    except InvalidProduct:
        return jsonify(serialize_form(form)), 400
    except DelistedProduct:
        return jsonify(dict(error="Delisted product")), 400

    summary = get_cart_summary(cart)

    return jsonify(dict(quantity=final_quantity, summary=summary))


# Keep cart total count public in jinja template
@app.context_processor
def cart_total_injector():
    cart = get_user_cart()
    summary = get_cart_summary(cart)
    return dict(current_cart=summary)