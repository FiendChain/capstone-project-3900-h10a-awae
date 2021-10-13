from flask import json, redirect, request, render_template, url_for, abort, jsonify
from flask import Blueprint

from .forms import ProductForm, serialize_form
from .temp_db import db, InvalidFileExtension
from .roles import admin_required

admin_bp = Blueprint('admin_bp', __name__, static_folder='static', static_url_path='/static', template_folder='templates')
admin_api_bp = Blueprint('admin_api_bp', __name__, static_folder='static', static_url_path='/static', template_folder='templates')

@admin_bp.route('/', methods=['GET'])
@admin_required
def home():
    return render_template("admin/home.html")

@admin_bp.route("/products", methods=['GET'])
@admin_required
def products():
    flat_products = list(db.products.values())
    return render_template("admin/products.html", products=flat_products)


@admin_bp.route("/products/add", methods=['GET'])
@admin_required
def add_product():
    form = ProductForm()
    return render_template("admin/add_product.html", form=form)


@admin_bp.route("/products/<string:id>/edit", methods=["GET"])
@admin_required
def edit_product(id):
    if id not in db.products:
        abort(404)
    
    product = db.products[id]
    form = ProductForm(data=product)
    return render_template("admin/edit_product.html", form=form, id=id)

# admin api endpoints
# used primary for database editing, adding and deletion
@admin_api_bp.route("/products/add", methods=['POST'])
@admin_required
def add_product():
    form = ProductForm()

    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 403

    print(f"Adding product: {form}")
    uid = db.gen_uuid()

    image_file = form.image.data

    if image_file:
        try:
            image_url = db.add_image(image_file)
        except InvalidFileExtension as ex:
            form.image.errors.append("Invalid file extension")
            return jsonify(serialize_form(form)), 403
    else:
        image_url = None
    
    product = {
        "id": uid,
        "name": form.name.data,
        "unit_price": form.unit_price.data,
        "category": form.category.data,
        "description": form.description.data,
        "est_delivery_amount": form.est_delivery_amount.data,
        "est_delivery_units": form.est_delivery_units.data,
        "in_stock": form.in_stock.data,
        "image_url": image_url,
    }

    db.products[uid] = product
    return jsonify(dict(redirect=url_for("admin_bp.products")))

@admin_api_bp.route("/products/<string:id>/edit", methods=["POST"]) 
@admin_required
def edit_product(id):
    if id not in db.products:
        abort(404)

    form = ProductForm()
    
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 403

    print(f"Editing product: {form}")
    product = db.products[id]

    image_file = form.image.data

    if image_file:
        try:
            image_url = db.add_image(image_file)
        except InvalidFileExtension as ex:
            form.image.errors.append("Invalid file extension")
            return jsonify(serialize_form(form)), 403
    elif not form.image_changed.data:
        image_url = product['image_url']
    else:
        image_url = None

    product = {
        "id": id,
        "name": form.name.data,
        "unit_price": form.unit_price.data,
        "category": form.category.data,
        "description": form.description.data,
        "est_delivery_amount": form.est_delivery_amount.data,
        "est_delivery_units": form.est_delivery_units.data,
        "in_stock": form.in_stock.data,
        "image_url": image_url,
    }

    db.products[id] = product
    return jsonify(dict(redirect=url_for("admin_bp.products")))

@admin_api_bp.route("/products/<string:id>/delete", methods=["POST"])
@admin_required
def delete_product(id):
    if id in db.products:
        print(f"Deleting product: {id}")
        del db.products[id]
        return jsonify({'success': True})
    
    abort(403)