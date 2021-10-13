from flask import json, redirect, request, render_template, url_for, abort, jsonify
from flask import Blueprint

from .forms import ProductForm, serialize_form
from .temp_db import db, InvalidFileExtension
from .roles import admin_required
from server import app, get_db

admin_bp = Blueprint('admin_bp', __name__, static_folder='static', static_url_path='/static', template_folder='templates')
admin_api_bp = Blueprint('admin_api_bp', __name__, static_folder='static', static_url_path='/static', template_folder='templates')

@admin_bp.route('/', methods=['GET'])
@admin_required
def home():
    return render_template("admin/home.html")

@admin_bp.route("/products", methods=['GET'])
@admin_required
def products():
    with app.app_context():
        db = get_db()
        products = db.search_product_by_name()
    return render_template("admin/products.html", products=products)


@admin_bp.route("/products/add", methods=['GET'])
@admin_required
def add_product():
    form = ProductForm()
    return render_template("admin/add_product.html", form=form)

# admin api endpoints
# used primary for database editing, adding and deletion
@admin_api_bp.route("/products/add", methods=['POST'])
@admin_required
def add_product():
    form = ProductForm()

    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 403

    print(f"Adding product: {form}")

    with app.app_context():
        db = get_db()
        image_url = db.gen_image_url(form.image.data, app)
        product = (
            form.name.data, form.unit_price.data, form.brand.data, form.category.data, form.description.data, form.delivery_days.data, form.warranty_days.data, form.stock.data, image_url
        )
        id = db.add("products", product)
        


    # if image_file:
    #     try:
    #         image_url = db.add_image(image_file)
    #     except InvalidFileExtension as ex:
    #         form.image.errors.append("Invalid file extension")
    #         return jsonify(serialize_form(form)), 403
    # else:
    #     image_url = None
    
    # product = {
    #     "id": uid,
    #     "name": form.name.data,
    #     "unit_price": form.unit_price.data,
    #     "brand": form.brand.data,
    #     "category": form.category.data,
    #     "description": form.description.data,
    #     "delivery_days": form.delivery_days.data,
    #     "warranty_days": form.warranty_days.data,
    #     "in_stock": form.in_stock.data,
    #     "image_url": image_url,
    # }

    # db.products[uid] = product
    return jsonify(dict(redirect=url_for("admin_bp.products")))

@admin_bp.route("/products/<string:id>/edit", methods=["GET"])
@admin_required
def edit_product(id):
    with app.app_context():
        db = get_db()
        product = db.get_entry_by_id("products", id)
    form = ProductForm(data=product)
    return render_template("admin/edit_product.html", form=form, id=id)

@admin_api_bp.route("/products/<string:id>/edit", methods=["POST"]) 
@admin_required
def edit_product(id):

    form = ProductForm()
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 403

    print(f"Editing product: {form}")
    with app.app_context():
        db = get_db()
        if form.image.data is None: # if admin does not change the image, use old url
            image_url = form.image_url.data
        else:
            image_url = db.gen_image_url(form.image.data, app)
        product = (
            id, form.name.data, form.unit_price.data, form.brand.data, form.category.data, form.description.data, form.delivery_days.data, form.warranty_days.data, form.stock.data, image_url
        )
        db.update("products", product, product) # also pass in new product as old product, as we only need the id of the old product to update table
    # product = db.products[id]

    # image_file = form.image.data

    # if image_file:
    #     try:
    #         image_url = db.add_image(image_file)
    #     except InvalidFileExtension as ex:
    #         form.image.errors.append("Invalid file extension")
    #         return jsonify(serialize_form(form)), 403
    # elif not form.image_changed.data:
    #     image_url = product['image_url']
    # else:
    #     image_url = None


    # db.products[id] = product
    return jsonify(dict(redirect=url_for("admin_bp.products")))

@admin_api_bp.route("/products/<string:id>/delete", methods=["POST"])
@admin_required
def delete_product(id):
    with app.app_context():
        db = get_db()
        if db.get_entry_by_id("products", id) is not []:
            db.delete_by_id("products", id)

            return jsonify({'success': True})
    
    abort(403)