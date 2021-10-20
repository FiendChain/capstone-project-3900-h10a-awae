"""
Routes for basic ecommerce functionalities
This includes browsing and visitng product pages
"""

from flask import json, redirect, request, render_template, url_for, jsonify, abort, session

from server import app, get_db
from .endpoints import user_bp, api_bp
from .forms import ProductSearchParams, serialize_form

# Product browsing
@user_bp.route('/', methods=["GET", "POST"])
def home():
    with app.app_context():
        db = get_db()
        products = db.get_random_entries("products", 5)
    return render_template("homepage.html", products=products)

@user_bp.route('/products/<string:id>', methods=['GET'])
def product_page(id):
    with app.app_context():
        db = get_db()
        product = db.get_entry_by_id("products", id)
    return render_template('product.html', product=product)

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

