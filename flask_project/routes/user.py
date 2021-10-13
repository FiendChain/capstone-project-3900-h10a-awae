from flask import redirect, request, render_template, url_for, jsonify, abort, session
from flask_login import login_user, current_user, logout_user
from flask import Blueprint
from flask_login.utils import login_required

from server import login_manager, app, get_db
from .temp_db import db, SessionCart
from .forms import LoginForm, RegisterForm, UserPurchaseForm, UserProfileLoginSecurityForm, serialize_form
from classes.flaskuser import FlaskUser

user_bp  = Blueprint('user_bp', __name__, static_folder='static', static_url_path='/static', template_folder='templates')
api_bp = Blueprint('api_bp', __name__)

# Product browsing
@user_bp.route('/', methods=["GET", "POST"])
def home():
    with app.app_context():
        db = get_db()
        products = db.get_random_entries("products", 5)
        print("Rendering homepage")
    return render_template("homepage.html", products=products)

@user_bp.route('/products/<string:id>', methods=['GET', 'POST'])
def product_page(id):
    with app.app_context():
        db = get_db()
        product = db.get_entry_by_id("products", id)
    return render_template('product.html', product=product)

@user_bp.route('/search', methods=['GET', 'POST'])
def search_page(filter):
    with app.app_context():
        db = get_db
        #db.search_product_by_name()
    pass


# Signin endpoints
@user_bp.route('/login', methods=['GET'])
def login():
    form = LoginForm()
    return render_template("login.html", form=form)
    
@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    return render_template('registration.html', form=form)

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("user_bp.login"))

# Perform login validation
@api_bp.route("/login", methods=["POST"])
def login():
    form = LoginForm()

    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 403

    if form.validate_on_submit():
        username = form.name.data
        password = form.password.data
        with app.app_context():
            db = get_db()
            valid = db.validate_user(username, password)

            # invalid credentials
            if valid == True:
                user = db.get_entries_by_heading("users", "username", username)[0]
                flask_user = FlaskUser(user["username"], True, True, False, chr(user["id"]), user["is_admin"])    # user id must be unicode
                print(f"User {flask_user.get_username()}logged in: {serialize_form(form)}")
                login_user(flask_user, remember=form.remember_me.data)
                return jsonify(dict(redirect=url_for("user_bp.home")))
            else:
                form.name.errors.append("Invalid credentials")
                form.password.errors.append("Invalid credentials")
                return jsonify(serialize_form(form)), 403

# Perform registration validation
@api_bp.route("/register", methods=["POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        with app.app_context():
            db = get_db()
            user_data = (form.username.data, form.password.data, form.email.data, form.phone.data, 0)   # 0 = user, 1 = admin
            try:
                db.add("users", user_data)
            except Exception as e:
                #print(serialize_form(form))
                form.username.errors.append("Username already taken")
                return jsonify(serialize_form(form)), 403

            print(f"User registered: {serialize_form(form)}")
            return jsonify(dict(redirect=url_for("user_bp.register")))
    
    return jsonify(serialize_form(form)), 403

# User account
@user_bp.route('/profile', methods=["GET"])
@login_required
def profile():
    return render_template("profile.html")

@user_bp.route('/profile/login_security', methods=["GET"])
@login_required
def profile_edit_login_security():
    form = UserProfileLoginSecurityForm()
    return render_template("profile/edit_login_security.html", form=form)

@api_bp.route('/profile/login_security', methods=['POST'])
@login_required
def profile_edit_login_security():
    form = UserProfileLoginSecurityForm()
    if form.validate_on_submit():
        # TODO: actually check to see that the form values can be applied to the database

        return jsonify(dict(redirect=url_for("user_bp.profile")))
    
    return jsonify(serialize_form(form)), 403

# Cart and purchasing
def validate_product_id(id):
    return id in db.products

# Depending on whether a user is logged in, we can store cart in flask-session or mock db
def get_user_cart():
    if not current_user.is_authenticated:
        cart = SessionCart(session)
    else:
        cart = current_user.cart

    cart.purge(validate_product_id)
    return cart

# Render the cart page
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


# Add product to cart
@api_bp.route('/transaction/add', methods=['POST'])
def product_add():
    form = UserPurchaseForm(meta=dict(csrf=False))
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 403

    if not validate_product_id(form.id.data):
        form.id.errors.append("Invalid product id")
        return jsonify(serialize_form(form)), 403

    cart = get_user_cart()
    cart.add_product(form.id.data, form.quantity.data)

    return jsonify(serialize_form(form))

# Update the quantity of a product in the cart
@api_bp.route('/transactions/update', methods=['POST'])
def product_update():
    form = UserPurchaseForm(meta=dict(csrf=False))
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 403
    
    if not validate_product_id(form.id.data):
        form.id.errors.append("Invalid product id")
        return jsonify(serialize_form(form)), 403

    cart = get_user_cart()
    cart.update_product(form.id.data, form.quantity.data)

    return jsonify(dict(quantity=form.quantity.data))

# TODO: Buy the product immediately
@api_bp.route('/transaction/buy', methods=['POST'])
def product_buy():
    form = request.form
    print(f'Buying: {form}')
    return jsonify(dict(success=True))

# Reloads and returns the User object for current session
@login_manager.user_loader
def load_user(id):
    with app.app_context():
        db = get_db()
        print("Load user id ", ord(id))
        user = db.get_entry_by_id("users", ord(id)) # convert unicode id back to int
        print(user)
        if user is None:
            return None
        flask_user = FlaskUser(user["username"], True, True, False, chr(user["id"]), user["is_admin"])
        return flask_user
