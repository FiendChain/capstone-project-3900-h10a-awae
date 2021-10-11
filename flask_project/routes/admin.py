# Store all routes here

from flask import Flask, json, redirect, request, render_template, url_for, send_from_directory, jsonify, abort
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask import g
from flask import Blueprint
from werkzeug.utils import secure_filename

from server import login_manager, app
import os
import uuid

admin_bp = Blueprint('admin_bp', __name__, static_folder='static', static_url_path='/static', template_folder='templates')

db_products = [
    {
        "id": "A232-109",
        "name": "Lite Latte",
        "cost": f"{10:.2f}",
        "est_delivery": "3 days",
        "in_stock": 10
    },
    {
        "id": "A232-222",
        "name": "Heavy Latte",
        "cost": f"{20:.2f}",
        "est_delivery": "2 days",
        "in_stock": 20
    },
    {
        "id": "A232-333",
        "name": "Dark Latte",
        "cost": f"{15:.2f}",
        "est_delivery": "5 days",
        "in_stock": 40
    }
]

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
    return render_template("admin/products.html", products=db_products)

@admin_bp.route("/products/add", methods=['POST', 'GET'])
def add_product():
    if request.method == 'GET':
        return render_template("admin/add_product.html")
    
    print(f"Adding product: {request.form}")
    print(request.files)

    form = request.form.to_dict(flat=True)

    files = request.files.to_dict(flat=True)
    if 'image' not in files:
        abort(403)

    file = files['image']
    if file.filename == '':
        abort(403)
    
    if '.' not in file.filename:
        abort(403)

    ext = os.path.splitext(file.filename)[1]
    rand_filename = f"{uuid.uuid4()}.{ext}"
    uid = uuid.uuid4()
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], rand_filename))
    
    product = {
        "name": form["name"],
        "cost": form["price"],
        "category": form["category"],
        "description": form["description"],
        "est_delivery": f"{form['est-delivery']} {form['est-delivery-units']}",
        "in_stock": 10,
        "image_url": rand_filename,
        "id": uid,
    }

    db_products.append(product)

    return redirect(url_for('admin_bp.products'))

@admin_bp.route("/products/<string:id>")
def product_page(id):
    if id not in db_products:
        abort(404)
    
    product = db_products[id]
    return render_template("admin/edit_product.html", product=product)

