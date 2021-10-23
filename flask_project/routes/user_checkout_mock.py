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
from db.checkout_db import checkout_db

@app.before_first_request
def seed_checkout_sessions():
    items = [(1,1),(2,3),(15,3),(10,5)]
    with app.app_context():
        id = "502d78b0-2025-4163-a873-3c1a25a25a60" 
        db = get_db()
        checkout_db.create_checkout(items, db, None, checkout_id=id)

# handle checkout on instant buy
@api_bp.route('/transaction/buy', methods=['POST'])
def product_buy():
    form = UserPurchaseForm(meta=dict(csrf=False))
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 403
    
    id = form.id.data
    quantity = form.quantity.data

    with app.app_context():
        db = get_db()
        checkout_id = checkout_db.create_checkout([(id, quantity)], db, current_user.get_id())

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
    
    if checkout.is_completed:
        return redirect(url_for("user_bp.checkout_status", checkout_id=checkout_id))

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
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 403
    
    if form.cc_name.data != "Hugh Mungus":
        form.cc_name.errors.append("Your name must be Hugh Mungus")
        return jsonify(serialize_form(form)), 403
    
    #TODO: Assign a the checkout session an order id
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

    try: 
        # TODO: replace with db id
        checkout.order_id = 1
    except CheckoutAlreadyCompleted:
        # just redirect to checkout status page
        pass

    res =  dict(redirect=url_for("user_bp.checkout_status", checkout_id=checkout_id))
    return jsonify(res), 200


# checkout status page
@user_bp.route("/checkout_status/<string:checkout_id>", methods=["GET"])
def checkout_status(checkout_id):
    with app.app_context():
        db = get_db()
        try:
            checkout = checkout_db.get_checkout(checkout_id, db)
        except KeyError as ex:
            abort(404)
        except CheckoutExpired as ex:
            abort(404)

    if checkout.user_id != current_user.get_id():
        abort(403)

    data = dict(
        is_success=True,
        checkout=checkout
    )
    return render_template("checkout_status.html", **data)