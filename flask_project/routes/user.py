# Store all routes here

from flask import Flask, json, redirect, request, render_template, url_for, send_from_directory, jsonify, abort
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask import g
from flask import Blueprint

from server import login_manager

from .temp_db import db


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

# User account
@user_bp.route('/cart', methods=['GET'])
def cart():
    products = db.products.values()

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

# Purchasing
@api_bp.route('/transaction/add', methods=['POST'])
def product_add():
    form = request.form
    print(f'Adding: {form}')

    return jsonify(dict(success=True))

@api_bp.route('/transactions/update', methods=['POST'])
def product_update():
    form = request.form
    # discard repeats of same input field
    data = form.to_dict(flat=True)
    print(f'Changing quantity: {data}')

    quantity = int(data['quantity'])
    if quantity > 10 or quantity < 0:
        return jsonify(**dict(quantity=2), error='Invalid quantity'), 403

    return jsonify(dict(quantity=quantity))

@api_bp.route('/transaction/buy', methods=['POST'])
def product_buy():
    form = request.form
    print(f'Buying: {form}')
    return jsonify(dict(success=True))

# Signin endpoints
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('registration.html')

@user_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("user_bp.login"))

# Reloads and returns the User object for current session
@login_manager.user_loader
def load_user(name):
    pass
