"""
Routes for login and registratioon
"""

from flask import json, redirect, request, render_template, url_for, jsonify, abort, session
from flask_login import login_user, logout_user, current_user
from flask_login.utils import login_required

from server import login_manager, app, get_db
from .endpoints import user_bp, api_bp
from .forms import LoginForm, RegisterForm, serialize_form
from classes.flaskuser import FlaskUser

import uuid


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
                flask_user = FlaskUser(user["username"], user["is_authenticated"], True, False, chr(user["id"]), user["is_admin"])    # user id must be unicode
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
            user_data = (form.username.data, form.password.data, form.email.data, form.phone.data, 0, 1)   # 0 = user, 1 = admin
            try:
                db.add("users", user_data)
            except Exception as e:
                form.username.errors.append("Username already taken")
                return jsonify(serialize_form(form)), 403

            print(f"User registered: {serialize_form(form)}")

            user = db.get_entries_by_heading("users", "username", user_data[0])[0]
            flask_user = FlaskUser(user["username"], user["is_authenticated"], True, False, chr(user["id"]), user["is_admin"])    # user id must be unicode
            print(f"User {flask_user.get_username()} registered and logged in")
            login_user(flask_user, remember=form.remember_me.data)
            return jsonify(dict(redirect=url_for("user_bp.home")))
    
    return jsonify(serialize_form(form)), 403

# Make sure a user is either given a guest account or is already logged in
@app.before_request
def create_guest_account():
    # if already logged in
    if current_user and current_user.get_id() is not None:
        return
    
    # attempt to get guest id from session
    try:
        guest_id = ord(session["guest_id"])
    except TypeError:
        guest_id = None
    except KeyError:
        guest_id = None

    if guest_id is not None:
        with app.app_context():
            db = get_db()
            user = db.get_entry_by_id("users", guest_id)
            # login the guest account
            if user is not None and not user["is_authenticated"]:
                flask_user = FlaskUser(user["username"], user["is_authenticated"], True, False, chr(user["id"]), user["is_admin"])
                login_user(flask_user, True)
                return

    # create guest account if not logged 
    with app.app_context():
        db = get_db()
        while True:
            id = str(uuid.uuid4())
            username = f"Guest#{id}"
            user_data = (username, "", "", "", 0, 0)
            try:
                db.add("users", user_data)
            except Exception as ex:
                continue
            break
    
    user = db.get_entries_by_heading("users", "username", username)[0]
    guest_id = chr(user["id"])
    flask_user = FlaskUser(user["username"], user["is_authenticated"], True, False, guest_id, user["is_admin"])    # user id must be unicode
    login_user(flask_user, remember=True)
    session["guest_id"] = guest_id
    session.modified = True


# Loads and returns the User object for current session
@login_manager.user_loader
def load_user(id):
    print(f"Loading user with id={id}")
    with app.app_context():
        db = get_db()
        try:
            user = db.get_entry_by_id("users", ord(id)) # convert unicode id back to int
        except:
            user = None
        
        if user is None:
            return None

        flask_user = FlaskUser(user["username"], user["is_authenticated"], True, False, chr(user["id"]), user["is_admin"])
        return flask_user