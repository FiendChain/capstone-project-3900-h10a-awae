from flask import json, redirect, request, render_template, url_for, jsonify, abort, session
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask import g
from flask import Blueprint

from server import login_manager
from .temp_db import db, SessionCart
from .forms import LoginForm, RegisterForm, UserPurchaseForm, serialize_form

user_bp  = Blueprint('user_bp', __name__, static_folder='static', static_url_path='/static', template_folder='templates')
api_bp = Blueprint('api_bp', __name__)

# Product browsing
@user_bp.route('/', methods=["GET", "POST"])
def home():
    products = db.products.values()
    return render_template("homepage.html", products=products)


@user_bp.route('/products/<string:id>', methods=['GET', 'POST'])
def product_page(id):
    if id not in db.products:
        abort(404)
    
    product = db.products[id]

    return render_template('product.html', product=product)

# Signin endpoints
@user_bp.route('/login', methods=['GET'])
def login():
    login_form = LoginForm()
    register_form = RegisterForm()
    return render_template("login.html", login_form=login_form, register_form=register_form)
    

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('registration.html')

@user_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("user_bp.login"))

@api_bp.route("/login", methods=["POST"])
def login():
    form = LoginForm()

    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 403

    if form.validate_on_submit():
        key = lambda u: u.username == form.name.data and u.password == form.password.data
        users =  [u for u in db.users.values() if key(u)]

        # invalid credentials
        if not users:
            form.name.errors.append("Invalid credentials")
            form.password.errors.append("Invalid credentials")
            return jsonify(serialize_form(form)), 403

    assert(len(users) == 1)
    user = users[0]

    print(f"User logged in: {serialize_form(form)}")
    login_user(user, remember=form.remember_me.data)
    return jsonify(dict(redirect=url_for("user_bp.home")))
    

@api_bp.route("/register", methods=["POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        print(f"User registered: {serialize_form(form)}")
        return jsonify(dict(redirect=url_for("user_bp.register")))
    
    return jsonify(serialize_form(form)), 403

def validate_product_id(id):
    return id in db.products

def get_user_cart():
    if not current_user.is_authenticated:
        cart = SessionCart(session)
    else:
        cart = current_user.cart

    cart.purge(validate_product_id)
    return cart

# User account
@user_bp.route('/cart', methods=['GET'])
def cart():
    cart = get_user_cart()
    products = []
    for id, quantity in cart.to_list():
        product = db.products[id]
        data = {**product, 'quantity': quantity}
        products.append(data)

    summary = {
        'total_cost': f'{10:.2f}',
        'shipping_cost': f'{6:.2f}'
    }

    payment_details = {
        'card_number_last_four': "0421",
        'method': 'PayPal'
    }

    data = dict(
        products=products, 
        summary=summary, 
        payment_details=payment_details)

    return render_template('cart.html', **data)

@user_bp.route('/profile', methods=["GET"])
def profile():
    return render_template("profile.html")

# Purchasing
@api_bp.route('/transaction/add', methods=['POST'])
def product_add():
    form = UserPurchaseForm(meta=dict(csrf=False))
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 403

    if not validate_product_id(form.id.data):
        form.id.errors.append("Invalid product id")
        return jsonify(serialize_form(form)), 403

    print(f"Adding item to cart {form.id.data} {form.quantity.data}")

    cart = get_user_cart()
    cart.add_product(form.id.data, form.quantity.data)

    return jsonify(serialize_form(form))

@api_bp.route('/transactions/update', methods=['POST'])
def product_update():
    form = UserPurchaseForm(meta=dict(csrf=False))
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 403
    
    if not validate_product_id(form.id.data):
        form.id.errors.append("Invalid product id")
        return jsonify(serialize_form(form)), 403

    print(f'Changing quantity: {form.id.data} {form.quantity.data}')

    cart = get_user_cart()
    cart.update_product(form.id.data, form.quantity.data)

    return jsonify(dict(quantity=form.quantity.data))

@api_bp.route('/transaction/buy', methods=['POST'])
def product_buy():
    form = request.form
    print(f'Buying: {form}')
    return jsonify(dict(success=True))

# Reloads and returns the User object for current session
@login_manager.user_loader
def load_user(id):
    return db.users.get(id, None)
