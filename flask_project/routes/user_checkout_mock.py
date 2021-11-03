"""
Routes for creating and ending a mock checkout session
"""

from flask import json, redirect, request, render_template, url_for, jsonify, abort
from flask_login import current_user

from server import app, get_db
from .endpoints import user_bp, api_bp
from .forms import UserPurchaseForm, PaymentCardForm, serialize_form
from .cart import  get_user_cart

from classes.checkout import CheckoutExpired, CheckoutAlreadyCompleted
from classes.order import Order, Payment, Billing
from db.checkout_db import checkout_db, order_db

# handle checkout on instant buy
@api_bp.route('/transaction/buy', methods=['POST'])
def product_buy():
    form = UserPurchaseForm(meta=dict(csrf=False))
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 400
    
    id = form.id.data
    quantity = form.quantity.data

    data = {"product_id": id, "quantity": quantity}

    with app.app_context():
        db = get_db()
        checkout_id = checkout_db.create_checkout([data], db, current_user.get_id())

    return redirect(url_for("user_bp.cart_checkout_billing", checkout_id=checkout_id))

# handle checkout on cart checkout
@user_bp.route("/checkout", methods=["POST"])
def cart_checkout():
    cart = get_user_cart()
    print(f"CART ITEMS: {cart.to_list()}")
    with app.app_context():
        db = get_db()
        checkout_id = checkout_db.create_checkout(cart.to_list(), db, current_user.get_id())
    # x = checkout_db.get_checkout(checkout_id, db)
    return redirect(url_for("user_bp.cart_checkout_billing", checkout_id=checkout_id))

# handle checkout billing screen
@user_bp.route("/checkout_billing/<string:checkout_id>", methods=["GET"])
def cart_checkout_billing(checkout_id):
    with app.app_context():
        db = get_db()
        try:
            checkout = checkout_db.get_checkout(checkout_id, db)
        except KeyError as ex:
            print(ex)
            abort(404)
        except CheckoutExpired as ex:
            print(ex)
            abort(404)
    
    if checkout.user_id != current_user.get_id():
        abort(403)
    
    if checkout.is_completed:
        return redirect(url_for("user_bp.order_page", id=checkout.order_id))
    


    # # Check if customer specified quantity is <= current stock in database
    # products = checkout.get_products()
    # error = False
    # error_msg = None
    # for product in products:
    #     customer_quantity = product["quantity"]
    #     db_quantity = db.get_entry_by_id("products", product["id"])
    #     print(f"cq {customer_quantity} dq {db_quantity}")
    #     if customer_quantity > db_quantity:
    #         error = True
    #         error_msg = f"Error, user specified quantity more than database stock for product id {product['id']}"
    #         print(error_msg)


    # TODO: Prefill with user details if available
    form = PaymentCardForm()
    data = dict(
        checkout=checkout,
        form=form,
        checkout_id=checkout_id,

    )


    return render_template("checkout.html", **data)

# payment validation 
@api_bp.route("/checkout_billing/<string:checkout_id>", methods=["POST"])
def cart_checkout_billing(checkout_id):
    form = PaymentCardForm()
    #TODO: Add additional payment validation here 
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 400

    with app.app_context():
        db = get_db()
        try:
            checkout = checkout_db.get_checkout(checkout_id, db)
        except KeyError as ex:
            print(ex)
            abort(404)
        except CheckoutExpired as ex:
            print(ex)
            abort(404)

    if checkout.user_id != current_user.get_id():
        abort(404)

    # if order already exists
    if checkout.order_id is not None:
        res =  dict(redirect=url_for("user_bp.order_page", id=checkout.order_id))
        return jsonify(res), 200

    # create order and redirect
    payment = (form.cc_name.data, form.cc_number.data, form.cc_expiry.data, form.cc_cvc.data)
    billing = (form.country.data, form.address.data, form.state.data, form.zip_code.data)
    payment_past_id = db.add("payment_past", payment)
    billing_past_id = db.add("billing_past", billing)

    order = (current_user.get_id(), payment_past_id, billing_past_id, checkout.total_cost, checkout.total_items)
    order_id = db.add("order2", order)
    for product in checkout.get_products():
        order_item = (order_id, product["id"])
        db.add("order2_item", order_item)


    checkout.order_id = order_id    # Automatically sets checkout.is_completed to true

    res =  dict(redirect=url_for("user_bp.order_page", id=order_id))
    
    return jsonify(res), 200

