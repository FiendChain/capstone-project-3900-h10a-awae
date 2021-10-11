# Store all routes here

from flask import Flask, json, redirect, request, render_template, url_for, send_from_directory, jsonify
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from server import app, login_manager
from flask import g

<<<<<<< HEAD
    
# The first page displayed upon startup
@app.route('/', methods = ["GET", "POST"])
def login():
    somedata = "passing in some post data"
    return render_template("homepage.html", somedata = somedata)
=======
import random
>>>>>>> wy_frontend

# Product browsing
@app.route('/', methods=["GET", "POST"])
def home():
    data = {
        'products': [
            {
                'image_url': f'/static/images/coffee_{i}.jpg',
                'product_url': url_for('product_page', id=f'coffee_{i}')
            } for i in range(1,4)
        ]
    }
    return render_template("homepage.html", **data)


@app.route('/products/<string:id>', methods=['GET', 'POST'])
def product_page(id):
    product = {
        'id': id,
        'name': id,
        'image_url': f'/static/images/{id}.jpg',
        'cost': f'{10.25:.2f}',
        'description': 'The finest lattee on the planet '*5
    }
    return render_template('product.html', product=product)

# User account
@app.route('/cart', methods=['GET'])
def cart():
    def get_product(i):
        return {
            'id': f'coffee_{i}',
            'name': f'coffee_{i}',
            'cost': f'{10.25:.2f}',
            'description': 'The finest lattee on the planet',
            'image_url': f'/static/images/coffee_{i}.jpg',
            'product_url': url_for('product_page', id=f'coffee_{i}'),
            'category': 'coffee',
            'status': 'In stock',
        }
    products = [get_product(i) for i in range(1,4)]

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
@app.route('/api_v1/transaction/add', methods=['POST'])
def product_add():
    form = request.form
    print(f'Adding: {form}')

    return jsonify(dict(success=True))

@app.route('/api_v1/transactions/update', methods=['POST'])
def product_update():
    form = request.form
    # discard repeats of same input field
    data = form.to_dict(flat=True)
    print(f'Changing quantity: {data}')

    quantity = int(data['quantity'])
    if quantity > 10 or quantity < 0:
        return jsonify(**dict(quantity=2), error='Invalid quantity'), 403

    return jsonify(dict(quantity=quantity))

@app.route('/api_v1/transaction/buy', methods=['POST'])
def product_buy():
    form = request.form
    print(f'Buying: {form}')
    return jsonify(dict(success=True))

# Signin endpoints
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('registration.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("login"))

# Reloads and returns the User object for current session
@login_manager.user_loader
def load_user(name):
    pass

# @app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        if db.conn is not None:
            db.conn.close()

<<<<<<< HEAD
=======
# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_db', None)
#     if db is not None:
#         db.close()
>>>>>>> wy_frontend
