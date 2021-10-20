"""
Routes for creating and ending a mock checkout session
"""

from flask import json, redirect, request, render_template, url_for, jsonify, abort
from flask_login import current_user

from server import app, get_db
from .endpoints import user_bp, api_bp
from .forms import UserPurchaseForm, PaymentCardForm, serialize_form
from .cart import validate_product_id, get_user_cart

import uuid

checkout_sessions = {}

def get_checkout_session(id):
    return checkout_sessions.get(id, None)

# array of product_id and quantity pairs
def create_checkout_session(data, session_id=None):
    products = []
    total_items = 0
    total_cost = 0
    with app.app_context():
        db = get_db()
        for id, quantity in data:
            product = db.get_entry_by_id("products", id)
            if product is None:
                continue

            total_items += quantity
            total_cost += product['unit_price'] * quantity
            products.append({**product, 'quantity': quantity})
    
    session = dict(products=products, total_items=total_items, total_cost=total_cost)
    if session_id is None:
        session_id = str(uuid.uuid4())
    checkout_sessions[session_id] = session
    return session_id

@app.before_first_request
def seed_checkout_sessions():
    create_checkout_session([(1,1),(2,3),(15,3),(10,5)], "502d78b0-2025-4163-a873-3c1a25a25a60")

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
        product = db.get_entry_by_id("products", id)
        if not product:
            form.id.errors.append("Invalid product id")
            return jsonify(serialize_form(form)), 403
    
    session_id = create_checkout_session([(id, quantity)])
    return redirect(url_for("user_bp.cart_checkout_billing", session_id=session_id))

# handle checkout on cart checkout
@user_bp.route("/checkout", methods=["POST"])
def cart_checkout():
    cart = get_user_cart()
    session_id = create_checkout_session(cart.to_list())
    return redirect(url_for("user_bp.cart_checkout_billing", session_id=session_id))

# handle checkout billing screen
@user_bp.route("/checkout_billing/<string:session_id>", methods=["GET"])
def cart_checkout_billing(session_id):
    session = get_checkout_session(session_id)
    if not session:
        abort(404)


    products = session['products']
    summary = dict(
        total_items=session['total_items'], 
        total_cost=session['total_cost'])

    # TODO: Prefill with user details if availabel
    form = PaymentCardForm()

    data = dict(
        products=products,
        summary=summary,
        form=form,
        session_id=session_id,
    )

    return render_template("checkout.html", **data)

# payment validation 
@api_bp.route("/checkout_billing/<string:session_id>", methods=["POST"])
def cart_checkout_billing(session_id):
    form = PaymentCardForm()
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 403
    
    if form.cc_name.data != "Hugh Mungus":
        form.cc_name.errors.append("Your name must be Hugh Mungus")
        return jsonify(serialize_form(form)), 403

    res =  dict(redirect=url_for("user_bp.checkout_status", session_id=session_id))
    return jsonify(res), 200


# checkout status page
@user_bp.route("/checkout_status/<string:session_id>", methods=["GET"])
def checkout_status(session_id):
    session = get_checkout_session(session_id)
    if not session:
        abort(404)

    summary = dict(
        total_items=session['total_items'], 
        total_cost=session['total_cost'])
    
    products = session['products']

    data = dict(
        is_success=True,
        products=products,
        summary=summary,
    )
    return render_template("checkout_status.html", **data)