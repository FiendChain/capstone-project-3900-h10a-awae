"""
Routes for basic ecommerce functionalities available to register or unregistered user
This includes browsing and visitng product pages and viewing orders
"""

from flask import json, redirect, request, render_template, url_for, jsonify, abort, session
from flask_login import current_user

from server import app, get_db
from .endpoints import user_bp, api_bp
from .forms import ProductSearchParams, serialize_form
import random

# Product browsing
@user_bp.route('/', methods=["GET", "POST"])
def home():
    with app.app_context():
        db = get_db()
        recommended_products = get_recommendations(db)

        # Aggregate all products and quantity user have bought
        # Display most popular products
        # (potentially) display how much was sold
        popular_items = db.get_random_entries("product", 12)
    data = dict(recommended_products=recommended_products, popular_items=popular_items)
    
    return render_template("homepage.html", **data)

@user_bp.route('/products/<string:id>', methods=['GET'])
def product_page(id):
    with app.app_context():
        db = get_db()
        product = db.get_entry_by_id("product", id)
        similar_items = db.get_random_entries("product", 12)
    return render_template('product.html', product=product, similar_items=similar_items)

@user_bp.route('/search', methods=['GET', 'POST'])
def search():
    with app.app_context():
        db = get_db()
        valid_categories = db.get_unique_values("product", "category")
        form = ProductSearchParams()
        dict_sort_by = {
            "price_low_to_high": "unit_price ASC",
            "price_high_to_low": "unit_price DESC"
        }
        sort_by = dict_sort_by[form.sort_type.data]
        products = db.search_product_by_name(form.name.data, form.categories.data, sort_by)
        for p in products:
            if p["is_deleted"]:
                products.remove(p)
    return render_template('search.html', products=products, categories=valid_categories, form=form)

def get_recommendations(db):
    recent_categories = []
    recommended_products = []
    window = 10 # Use last X product's categories bought for recommendation
    # Get list of orders by user
    num_recommendations = 4
    orders = db.get_entries_by_heading("order2", "user_id", current_user.get_id(), "id DESC")   # Get most recent entries
    for order in orders:
        order_items = db.get_entries_by_heading("order2_item", "order2_id", order["id"])
        for order_item in order_items:
            # Get product matching to order item
            product = db.get_entry_by_id("product", order_item["product_id"])
            if not product["is_deleted"]:
                print(product["name"], product["category"])
                recent_categories.append(product["category"])
        # Use minimum last 10 products bought
        if len(recent_categories) >= window:
            break

    # If user bought less than 4 products, change number of recommendations to the number of products user has bought (0-3 recommendations)
    if len(recent_categories) < num_recommendations:
        num_recommendations = len(recent_categories)
    
    sampled_categories = random.sample(recent_categories, num_recommendations)
    sampled_categories = dict((x,sampled_categories.count(x)) for x in set(sampled_categories))

    for category, count in sampled_categories.items():
        products = db.get_random_entries_with_condition("product", "category", category, count)
        for p in products:
            recommended_products.append(p)
    return recommended_products