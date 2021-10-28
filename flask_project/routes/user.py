"""
Routes for basic ecommerce functionalities available to register or unregistered users
This includes browsing and visitng product pages and viewing orders
"""

from flask import json, redirect, request, render_template, url_for, jsonify, abort, session
from flask_login import current_user

from server import app, get_db
from .endpoints import user_bp, api_bp
from .forms import ProductSearchParams, serialize_form

from db.checkout_db import order_db
import datetime

# Product browsing
@user_bp.route('/', methods=["GET", "POST"])
def home():
    with app.app_context():
        db = get_db()
        recommended_products = db.get_random_entries("products", 16)
        popular_items = db.get_random_entries("products", 12)
    
    data = dict(recommended_products=recommended_products, popular_items=popular_items)
    
    return render_template("homepage.html", **data)

@user_bp.route('/products/<string:id>', methods=['GET'])
def product_page(id):
    with app.app_context():
        db = get_db()
        product = db.get_entry_by_id("products", id)
        similar_items = db.get_random_entries("products", 12)
    return render_template('product.html', product=product, similar_items=similar_items)

@user_bp.route('/search', methods=['GET', 'POST'])
def search():

    with app.app_context():
        db = get_db()
        valid_categories = db.get_unique_values("products", "category")
        form = ProductSearchParams()
        print(serialize_form(form))
        dict_sort_by = {
            "price_low_to_high": "unit_price ASC",
            "price_high_to_low": "unit_price DESC"
        }
        sort_by = dict_sort_by[form.sort_type.data]
        products = db.search_product_by_name(form.name.data, form.categories.data, sort_by)
    return render_template('search.html', products=products, categories=valid_categories, form=form)

@user_bp.route('/profile/orders', methods=['GET'])
def profile_orders():
    orders = order_db.get_orders_by_user_id(current_user.get_id())
    print(orders)
    return render_template('orders.html', orders=orders)

@user_bp.route('/order/<string:id>', methods=['GET'])
def order_page(id):
    order = order_db.get_order(id)
    if order is None:
        abort(404)
    
    if order.user_id != current_user.get_id():
        abort(403)


    data = dict(
        is_success=True,
        order=order,
    )
    return render_template("order_page.html", **data)

