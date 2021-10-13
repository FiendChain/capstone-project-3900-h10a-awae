from flask import redirect, request, render_template, url_for, abort
from flask import g
from flask import Blueprint

from flask import jsonify

from server import app
import os
import uuid

from .forms import ProductForm, LoginForm, serialize_form
from .temp_db import db

admin_bp = Blueprint('admin_bp', __name__, static_folder='static', static_url_path='/static', template_folder='templates')
admin_api_bp = Blueprint('admin_api_bp', __name__, static_folder='static', static_url_path='/static', template_folder='templates')

@admin_bp.route('/', methods=['GET'])
def home():
    return render_template("admin/home.html")

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == "GET":
        return render_template("admin/login.html", form=form)
    
    if form.validate_on_submit():
        print(f"Logging in user: {serialize_form(form)}")
        return jsonify(dict(redirect=url_for("admin_bp.home"))) 
    
    return jsonify(serialize_form(form)), 403

@admin_bp.route("/products", methods=['GET'])
def products():
    flat_products = list(db.products.values())
    return render_template("admin/products.html", products=flat_products)


@admin_bp.route("/products/add", methods=['GET'])
def add_product():
    form = ProductForm()
    return render_template("admin/add_product.html", form=form)


@admin_bp.route("/products/<string:id>/edit", methods=["GET"])
def edit_product(id):
    if id not in db.products:
        abort(404)
    
    product = db.products[id]
    form = ProductForm(data=product)
    return render_template("admin/edit_product.html", form=form, id=id)

# admin api endpoints
# used primary for database editing, adding and deletion
@admin_api_bp.route("/products/add", methods=['POST'])
def add_product():
    form = ProductForm()

    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 403

    print(f"Adding product: {form}")
    uid = db.gen_uuid()

    image_file = form.image.data
    file_exists = image_file and image_file.filename != '' and '.' in image_file.filename

    if file_exists:
        ext = os.path.splitext(image_file.filename)[1]
        rand_filename = f"{uuid.uuid4()}.{ext}"
        image_file.save(os.path.join(app.config['UPLOADED_IMAGES_DEST'], rand_filename))
        image_url = f"/static/uploads/images/{rand_filename}"
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
def edit_product(id):
    if id not in db.products:
        abort(404)

    form = ProductForm()
    
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 403

    print(f"Editing product: {form}")
    product = db.products[id]

    image_file = form.image.data
    file_exists = image_file and image_file.filename != '' and '.' in image_file.filename

    if file_exists and form.image_changed.data:
        ext = os.path.splitext(image_file.filename)[1]
        rand_filename = f"{uuid.uuid4()}.{ext}"
        image_file.save(os.path.join(app.config['UPLOADED_IMAGES_DEST'], rand_filename))
        image_url = f"/static/uploads/images/{rand_filename}"
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
def delete_product(id):
    if id in db.products:
        print(f"Deleting product: {id}")
        del db.products[id]
        return jsonify({'success': True})
    
    abort(403)