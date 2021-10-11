# Store all routes here

from flask import Flask, json, redirect, request, render_template, url_for, send_from_directory, jsonify, abort
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask import g
from flask import Blueprint

from server import login_manager, app
import os
import uuid

from .forms import ProductForm

admin_bp = Blueprint('admin_bp', __name__, static_folder='static', static_url_path='/static', template_folder='templates')

db_products = {
    "A232-109": {
        "name": "Lite Latte",
        "cost": f"{10:.2f}",
        "est_delivery": "3 days",
        "in_stock": 10,
        "category": "coffee",
        "image_url": "/static/images/coffee_1.jpg"
    }
}

@admin_bp.route('/', methods=['GET'])
def home():
    return render_template("admin/home.html")

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("admin/login.html")
    
    return redirect(url_for("admin_bp.home"))

@admin_bp.route("/products", methods=['GET'])
def products():
    flat_products = [{"id":uid, **v} for uid, v in db_products.items()]
    return render_template("admin/products.html", products=flat_products)

@admin_bp.route("/products/add", methods=['POST', 'GET'])
def add_product():
    form = ProductForm()

    if not form.validate_on_submit():
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(err)
        return render_template("admin/add_product.html", form=form)

    print(f"Adding product: {form}")

    while (uid := str(uuid.uuid4())[:7]) in db_products:
        pass

    f = form.image.data

    ext = os.path.splitext(f.filename)[1]
    rand_filename = f"{uuid.uuid4()}.{ext}"
    f.save(os.path.join(app.config['UPLOADED_IMAGES_DEST'], rand_filename))
    image_url = f"/static/uploads/{rand_filename}"
    
    product = {
        "name": form.name.data,
        "cost": form.unit_price.data,
        "category": form.category.data,
        "description": form.description.data,
        "est_delivery": f"{form.est_delivery_amount.data} {form.est_delivery_units.data}",
        "in_stock": 10,
        "image_url": image_url,
    }

    db_products[uid] = product
    return redirect(url_for('admin_bp.products'))

@admin_bp.route("/products/<string:id>")
def product_page(id):
    if id not in db_products:
        abort(404)
    
    product = db_products[id]
    return render_template("admin/edit_product.html", product=product)

