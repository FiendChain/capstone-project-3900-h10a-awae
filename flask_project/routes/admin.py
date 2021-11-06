from flask import json, redirect, request, render_template, url_for, abort, jsonify

from server import app, get_db
from .endpoints import admin_bp, admin_api_bp

from .forms import ProductForm, serialize_form
from .roles import admin_required

@admin_bp.route('/', methods=['GET'])
@admin_required
def home():
    return redirect(url_for("admin_bp.products"))
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
    with app.app_context():
        db = get_db()
        valid_categories = db.get_unique_values("products", "category")
    return render_template("admin/add_product.html", form=form, categories=valid_categories)

# admin api endpoints
# used primary for database editing, adding and deletion
@admin_api_bp.route("/products/add", methods=['POST'])
@admin_required
def add_product():
    form = ProductForm()

    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 400

    with app.app_context():
        db = get_db()
        if form.image.data and form.image_changed.data:
            image_url = db.gen_image_url(form.image.data, app)
        else:
            image_url = None

        product = (
            form.name.data, form.unit_price.data, form.brand.data, form.category.data, 
            form.description.data, form.delivery_days.data, form.warranty_days.data, form.stock.data, 
            image_url, form.is_deleted.data
        )
        id = db.add("products", product)

    return redirect(url_for("admin_bp.products"))

@admin_bp.route("/products/<string:id>/edit", methods=["GET"])
@admin_required
def edit_product(id):
    with app.app_context():
        db = get_db()
        product = db.get_entry_by_id("products", id)
        if not product:
            abort(404)
        valid_categories = db.get_unique_values("products", "category")

    form = ProductForm(data=product)
    return render_template("admin/edit_product.html", form=form, id=id, categories=valid_categories)

@admin_api_bp.route("/products/<string:id>/edit", methods=["POST"]) 
@admin_required
def edit_product(id):
    with app.app_context():
        db = get_db()
        product = db.get_entry_by_id("products", id)
        if product is None:
            abort(404)

    form = ProductForm()
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 400

    with app.app_context():
        db = get_db()
        if form.image_changed.data and form.image.data:
            image_url = db.gen_image_url(form.image.data, app)
        elif form.image_changed.data and not form.image.data:
            image_url = ""
        else:
            image_url = product["image_url"]
            
        product = (
            id, form.name.data, form.unit_price.data, form.brand.data, form.category.data, 
            form.description.data, form.delivery_days.data, form.warranty_days.data, form.stock.data, 
            image_url, form.is_deleted.data
        )

        db.update("products", product, product)

    return redirect(url_for("admin_bp.edit_product", id=id))

@admin_api_bp.route("/products/<string:id>/delete", methods=["POST"])
@admin_required
def delete_product(id):
    with app.app_context():
        db = get_db()

    product = db.get_entry_by_id("products", id)
    if not product:
        abort(404)
    
    product_old = list(product.values())
    product["is_deleted"] = 1 
    product_new = list(product.values())
    db.update("products", product_old, product_new)

    return redirect(url_for("admin_bp.products"))

@admin_api_bp.route("/products/<string:id>/relist", methods=["POST"])
@admin_required
def relist_product(id):
    with app.app_context():
        db = get_db()

    product = db.get_entry_by_id("products", id)
    if not product:
        abort(404)
    
    product_old = list(product.values())
    product["is_deleted"] = 0 
    product_new = list(product.values())
    db.update("products", product_old, product_new)

    return redirect(url_for("admin_bp.products"))