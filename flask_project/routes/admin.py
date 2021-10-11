from flask import redirect, request, render_template, url_for, abort
from flask import g
from flask import Blueprint

from flask import jsonify

from server import app
import os
import uuid

from .forms import ProductForm

def serialize_form(form):
    data = [] 
    for field in form:
        name = field.id
        value = field.data
        errors = field.errors

        if isinstance(value, str):
            data.append({"name": name, "value": value, "errors": errors})

    return data

admin_bp = Blueprint('admin_bp', __name__, static_folder='static', static_url_path='/static', template_folder='templates')
admin_api_bp = Blueprint('admin_api_bp', __name__, static_folder='static', static_url_path='/static', template_folder='templates')

db_products = {
    "A232-109": {
        "name": "Lite Latte",
        "unit_price": 10.20,
        "est_delivery_amount": 3,
        "est_delivery_units": "days",
        "in_stock": 10,
        "category": "coffee",
        "image_url": "/static/images/coffee_1.jpg",
        "description": "A deliciously light latte that makes you moist"
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


@admin_bp.route("/products/add", methods=['GET'])
def add_product():
    form = ProductForm()
    return render_template("admin/add_product.html", form=form)

@admin_api_bp.route("/products/add", methods=['POST'])
def add_product():
    form = ProductForm()

    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 403

    print(f"Adding product: {form}")
    while (uid := str(uuid.uuid4())[:7]) in db_products:
        pass

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
        "name": form.name.data,
        "unit_price": form.unit_price.data,
        "category": form.category.data,
        "description": form.description.data,
        "est_delivery_amount": form.est_delivery_amount.data,
        "est_delivery_units": form.est_delivery_units.data,
        "in_stock": form.in_stock.data,
        "image_url": image_url,
    }

    db_products[uid] = product
    return redirect(url_for("admin_bp.products"))
    # return jsonify(dict(success=True))


@admin_bp.route("/products/<string:id>/edit", methods=["GET"])
def edit_product(id):
    if id not in db_products:
        abort(404)
    
    product = db_products[id]
    form = ProductForm(data={'id':id, **product})
    return render_template("admin/edit_product.html", form=form, id=id)

@admin_api_bp.route("/products/<string:id>/edit", methods=["POST"]) 
def edit_product(id):
    if id not in db_products:
        abort(404)

    form = ProductForm()
    
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 403

    print(f"Editing product: {form}")
    product = db_products[id]

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
        "name": form.name.data,
        "unit_price": form.unit_price.data,
        "category": form.category.data,
        "description": form.description.data,
        "est_delivery_amount": form.est_delivery_amount.data,
        "est_delivery_units": form.est_delivery_units.data,
        "in_stock": form.in_stock.data,
        "image_url": image_url,
    }

    db_products[id] = product
    return jsonify(dict(success=True))

@admin_api_bp.route("/products/<string:id>/delete", methods=["POST"])
def delete_product(id):
    if id in db_products:
        print(f"Deleting product: {id}")
        del db_products[id]
        return jsonify({'success': True})
    
    abort(403)