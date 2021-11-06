"""
Routes for basic ecommerce functionalities available to register or unregistered users
This includes browsing and visitng product pages and viewing orders
"""

from flask import json, redirect, request, render_template, url_for, jsonify, abort, session, flash
from flask_login import current_user

from server import app, get_db
from .endpoints import user_bp, api_bp

from classes.order import Order
from classes.cart import TempCart, InvalidProduct, OutOfStock, DelistedProduct
from classes.cafepass import get_cafepass, CafepassInfo

from db.checkout_db import checkout_db

@user_bp.route('/profile/orders', methods=['GET'])
def profile_orders():
    with app.app_context():
        db = get_db()

    orders_db = db.get_entries_by_heading("order2", "user_id", current_user.get_id())
    orders = []
    for order_db in orders_db:
        orders.append(Order(order_db['id']))

    return render_template('orders.html', orders=orders)

# Display order information
@user_bp.route('/order/<string:id>', methods=['GET'])
def order_page(id):
    try:
        order = Order(id)
    except KeyError:
        abort(404)
    
    if order.user_id != current_user.get_id():
        abort(403)

    return render_template("order_page.html", order=order)

# Create a checkout with our order items
@api_bp.route('/order/<string:id>/checkout', methods=['POST', 'GET'])
def create_checkout_from_order(id):
    try:
        order = Order(id)
    except KeyError:
        abort(404)

    if order.user_id != current_user.get_id():
        abort(403)

    # create cart 
    cart = TempCart()
    for item in order.items:
        try:
            cart.add_product(item.product['id'], item.quantity)
        except InvalidProduct:
            continue
        except OutOfStock:
            continue
        except DelistedProduct:
            continue
    
    # if empty then do nothing
    if not cart.items:
        flash("No available items in order", "error")
        abort(400)
    
    with app.app_context():
        db = get_db()

    # get cafepass discount
    cafepass = get_cafepass()
    if cafepass:
        discount = CafepassInfo(cafepass, db).frac_discount
    else:
        discount = 0

    checkout_id = checkout_db.create_checkout(cart.items, db, discount, current_user.get_id(), is_cart=False)
    return redirect(url_for("user_bp.cart_checkout_billing", checkout_id=checkout_id))
    

    

