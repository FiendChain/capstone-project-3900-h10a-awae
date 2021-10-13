from flask import json, redirect, request, render_template, url_for, jsonify, abort, session
from flask_login import login_user, current_user, logout_user
from flask import Blueprint
from flask_login.utils import login_required

from server import login_manager, app, get_db
from .temp_db import db, SessionCart
from .forms import LoginForm, RegisterForm, UserPurchaseForm, UserProfileLoginSecurityForm, ProductSearchParams, serialize_form
from classes.flaskuser import FlaskUser

user_bp  = Blueprint('user_bp', __name__, static_folder='static', static_url_path='/static', template_folder='templates')
api_bp = Blueprint('api_bp', __name__)

# Product browsing
@user_bp.route('/', methods=["GET", "POST"])
def home():
    with app.app_context():
        db = get_db()
        products = db.get_random_entries("products", 5)
    return render_template("homepage.html", products=products)

@user_bp.route('/products/<string:id>', methods=['GET'])
def product_page(id):
    with app.app_context():
        db = get_db()
        product = db.get_entry_by_id("products", id)
    return render_template('product.html', product=product)

@user_bp.route('/search', methods=['GET', 'POST'])
def search():

    with app.app_context():
        db = get_db()
        valid_categories = db.get_unique_values("products", "category")
        form = ProductSearchParams()
        print(serialize_form(form))
        dict_sort_by = {
            "price_low_to_high": "unit_price ASC",
            "price_high_to_low": "unit_price DESC"
        }
        sort_by = dict_sort_by[form.sort_type.data]
        products = db.search_product_by_name(form.name.data, form.categories.data, sort_by)
    return render_template('search.html', products=products, categories=valid_categories, form=form)

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
                x = user["username"]    # passed in as string but for some reason flaskuser will output as tuple
                #print(x)
                flask_user = FlaskUser(x, True, True, False, chr(user["id"]), user["is_admin"])    # user id must be unicode
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

            user = db.get_entries_by_heading("users", "username", user_data[0])[0]
            flask_user = FlaskUser(user["username"], True, True, False, chr(user["id"]), user["is_admin"])    # user id must be unicode
            print(f"User {flask_user.get_username()} registered and logged in")
            login_user(flask_user, remember=form.remember_me.data)
            return jsonify(dict(redirect=url_for("user_bp.home")))
    
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
    id = ord(current_user.get_id()) # unicode to int
    with app.app_context():
        db = get_db()
        user = db.get_entry_by_id("users", id)
        form.email.data = user["email"]
        form.phone.data = user["phone"]
    return render_template("profile/edit_login_security.html", form=form)

@api_bp.route('/profile/login_security', methods=['POST'])
@login_required
def profile_edit_login_security():
    form = UserProfileLoginSecurityForm()
    if form.validate_on_submit():
        id = ord(current_user.get_id()) # unicode to int
        with app.app_context():
            db = get_db()
            user = db.get_entry_by_id("users", id)
            if not db.validate_user(user["username"], form.password.data): # If entered password does not match password in database, return error
                form.password.errors.append("Incorrect password")
                return jsonify(serialize_form(form)), 403

            # Create new user tuple and update old entry in db
            print("new password: ", form.new_password.data)
            user_old = ()
            for value in user:
                user_old += (value, )
            user_new = (user["id"], user["username"], form.new_password.data, form.email.data, form.phone.data, user["is_admin"])
            db.update("users", user_old, user_new)
        return jsonify(dict(redirect=url_for("user_bp.profile")))
    return jsonify(serialize_form(form)), 403

# Cart and purchasing
def validate_product_id(id):
    with app.app_context():
        db = get_db()
        product = db.get_entry_by_id("products", id)
    
    if product:
        return True
    return False

def get_cart_summary(cart):
    total_items = 0
    total_cost = 0
    with app.app_context():
        db = get_db()
        for id, quantity in cart.to_list():
            product = db.get_entry_by_id("products", id)
            total_items += quantity
            total_cost += quantity*product['unit_price']
    return {"total_items": total_items, "total_cost": total_cost}

# Depending on whether a user is logged in, we can store cart in flask-session or mock db
def get_user_cart():
    cart = SessionCart(session)

    # TODO: Replace this with the cart in sql database when done
    # if not current_user.is_authenticated:
    #     cart = SessionCart(session)
    # else:
    #     cart = current_user.cart

    cart.purge(validate_product_id)
    return cart

# Render the cart page
@user_bp.route('/cart', methods=['GET'])
def cart():
    cart = get_user_cart()
    products = []

    with app.app_context():
        db = get_db()
        for id, quantity in cart.to_list():
            product = db.get_entry_by_id("products", id)
            data = {**product, 'quantity': quantity}
            products.append(data)

    data = dict(
        products=products, 
        summary=get_cart_summary(cart))

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
    summary = get_cart_summary(cart)

    return jsonify(dict(quantity=form.quantity.data, summary=summary))

# TODO: Buy the product immediately
@api_bp.route('/transaction/buy', methods=['POST'])
def product_buy():
    form = request.form
    print(f'Buying: {form}')
    return jsonify(dict(success=True))

# TODO: handle cart checkout
@user_bp.route('/checkout', methods=['GET'])
def cart_checkout():
    print("Buying everything inside the cart")
    cart = get_user_cart()
    cart.empty()
    return redirect(url_for("user_bp.cart"))


# Reloads and returns the User object for current session
@login_manager.user_loader
def load_user(id):
    with app.app_context():
        db = get_db()
        user = db.get_entry_by_id("users", ord(id)) # convert unicode id back to int
        if user is None:
            return None
        flask_user = FlaskUser(user["username"], True, True, False, chr(user["id"]), user["is_admin"])
        return flask_user
