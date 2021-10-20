"""
Routes for creating and ending a mock checkout session
"""

from flask import json, redirect, request, render_template, url_for, jsonify, abort
from flask_login import current_user

from server import app, get_db
from .endpoints import user_bp, api_bp
from .forms import UserPurchaseForm, serialize_form
from .cart import validate_product_id, get_user_cart

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

    product.update(quantity=quantity)
    total_items = quantity
    total_cost = quantity * product['unit_price']

    data = dict(
        is_success=True,
        products=[product],
        summary=dict(total_cost=total_cost, total_items=total_items),
    )

    return render_template("checkout_status.html", **data)

# handle checkout on cart checkout
@user_bp.route("/checkout", methods=["POST"])
def cart_checkout():
    return redirect(url_for("user_bp.checkout_status"))

# checkout status page
@user_bp.route("/checkout_status", methods=["GET"])
def checkout_status():
    products = []
    total_items = 0
    total_cost = 0
    with app.app_context():
        db = get_db()
        cart = get_user_cart()
        for id, quantity in cart.to_list():
            product = db.get_entry_by_id("products", id)
            if product is None:
                continue

            total_items += quantity
            total_cost += product['unit_price'] * quantity
            products.append({**product, 'quantity': quantity})

    summary = dict(total_items=total_items, total_cost=total_cost)

    data = dict(
        is_success=True,
        products=products,
        summary=summary,
    )
    return render_template("checkout_status.html", **data)