"""
Routes for login and registratioon
"""

from flask import json, redirect, request, render_template, url_for, jsonify, abort, session
from flask_login import login_user, logout_user, current_user
from flask_login.utils import login_required

from server import login_manager, app, get_db
from .endpoints import user_bp, api_bp
from .forms import LoginForm, RegisterForm, api_redirect, serialize_form

from classes.account import get_login_user, create_registered_user
from classes.account import get_guest_account, create_guest_account
from classes.account import get_flask_user_from_db, UsernameTaken

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
        return jsonify(serialize_form(form)), 400
    
    flask_user = get_login_user(form.name.data, form.password.data)

    if not flask_user:
        form.name.errors.append("Invalid credentials")
        form.password.errors.append("Invalid credentials")
        return jsonify(serialize_form(form)), 400

    login_user(flask_user, remember=form.remember_me.data)
    return api_redirect(url_for("user_bp.home"))

# Perform registration validation
@api_bp.route("/register", methods=["POST"])
def register():
    form = RegisterForm()
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 400
    
    try:
        flask_user = create_registered_user(
            form.username.data, form.password.data,
            form.email.data, form.phone.data)
    except UsernameTaken:
        form.username.errors.append("Username already taken")
        return jsonify(serialize_form(form)), 400

    login_user(flask_user, remember=form.remember_me.data)
    return api_redirect(url_for("user_bp.home"))
    

# Make sure a user is either given a guest account or is already logged in
@app.before_request
def default_guest_login():
    # if already logged in
    if current_user and current_user.get_id() is not None:
        return
    
    # attempt to get guest id from session
    try:
        guest_id = session["guest_id"]
        guest_id = int(guest_id)
    except TypeError:
        guest_id = None
    except KeyError:
        guest_id = None

    # attempt to login a guest user if their id is available
    if guest_id is not None:
        flask_user = get_guest_account(guest_id)
        if flask_user:
            login_user(flask_user, remember=True)
            return
        
    flask_user = create_guest_account()
    login_user(flask_user, remember=True)
    session["guest_id"] = flask_user.get_id()
    session.modified = True

# Loads and returns the User object for current session
@login_manager.user_loader
def load_user(id):
    with app.app_context():
        db = get_db()

    try:
        user = db.get_entry_by_id("users", id)
    except:
        user = None
        
    if user is None:
        return None

    flask_user = get_flask_user_from_db(user)
    return flask_user