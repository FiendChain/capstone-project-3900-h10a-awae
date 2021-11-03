"""
Routes for creating and ending a mock checkout session
"""

from flask import json, redirect, request, render_template, url_for, jsonify, abort
from flask_login import current_user

from server import app, get_db
from .endpoints import user_bp, api_bp
from .forms import UserPurchaseForm, PaymentCardForm, serialize_form, valid_states
from .cart import  get_user_cart

from classes.checkout import CheckoutExpired, CheckoutAlreadyCompleted
from classes.order import Order, Payment, Billing
from db.checkout_db import checkout_db, order_db

import random

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

    with app.app_context():
        db = get_db()
        checkout_id = checkout_db.create_checkout(cart.to_list(), db, current_user.get_id())
    
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
    if checkout.is_completed:
        return redirect(url_for("user_bp.order_page", id=checkout.order_id))

    # NOTE: Guest user placeholder for demonstration
    if not current_user.is_authenticated:
        default_billing_info = dict(
            country="Australia",
            address="Guest Address #1",
            state=random.choice(valid_states),
            zip_code="1234"
        )

        default_payment_info = dict(
            cc_name="Guest Name #1",
            cc_number="4242 4242 4242 4242",
            cc_expiry="01 / 26",
            cc_cvc="123" 
        )
    # TODO: Prefill with user details if available
    # TODO: Replace this with a more secure method of storage and loading
    else:
        default_billing_info = None
        default_payment_info = None

    form = PaymentCardForm()
    data = dict(
        checkout=checkout,
        form=form,
        checkout_id=checkout_id,
        default_billing_info=default_billing_info,
        default_payment_info=default_payment_info,
        valid_states=valid_states
    )


    return render_template("checkout.html", **data)

# payment validation 
@api_bp.route("/checkout_billing/<string:checkout_id>", methods=["POST"])
def cart_checkout_billing(checkout_id):
    form = PaymentCardForm()
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
    payment = Payment(
        form.cc_name.data, form.cc_number.data, 
        form.cc_expiry.data, form.cc_cvc.data)
    
    billing = Billing(
        form.country.data, form.address.data,
        form.state.data, form.zip_code.data
    )

    # TODO: Handle saving of user data for checkout
    if current_user.is_authenticated:
        if form.remember_billing.data:
            print("TODO: Save billing information")
        if form.remember_payment.data:
            print("TODO: Save payment info")

    order = Order(current_user.get_id(), checkout.products, payment, billing)
    order_id = order_db.add_order(order)
    checkout.order_id = order_id

    res =  dict(redirect=url_for("user_bp.order_page", id=order_id))
    
    return jsonify(res), 200

