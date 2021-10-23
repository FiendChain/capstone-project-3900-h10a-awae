"""
Routes for a user's profile specific information
"""

from flask import redirect, request, render_template, url_for, jsonify, abort, session
from flask_login import current_user
from flask_login.utils import login_required

from server import app, get_db
from .endpoints import user_bp, api_bp
from .forms import UserProfileLoginSecurityForm, serialize_form

import datetime

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
                return jsonify(serialize_form(form)), 400

            # Create new user tuple and update old entry in db
            print("new password: ", form.new_password.data)
            user_old = ()
            for value in user:
                user_old += (value, )
            user_new = (user["id"], user["username"], form.new_password.data, form.email.data, form.phone.data, user["is_admin"])
            db.update("users", user_old, user_new)
        return jsonify(dict(redirect=url_for("user_bp.profile")))
    return jsonify(serialize_form(form)), 400

@user_bp.route('/profile/orders', methods=['GET'])
@login_required
def profile_orders():
    with app.app_context():
        db = get_db()
        orders = [
            {
                "time_placed": datetime.datetime.now(),
                "delivery_date": datetime.datetime.now(),
                "products": list(filter(lambda x: x is not None, (db.get_entry_by_id("products", i) for i in range(1,5)))),
            },
            {
                "time_placed": datetime.datetime.now(),
                "products": list(filter(lambda x: x is not None, (db.get_entry_by_id("products", i) for i in range(10,12)))),
            },
            {
                "cancelled": True,
                "time_placed": datetime.datetime.now(),
                "products": list(filter(lambda x: x is not None, (db.get_entry_by_id("products", i) for i in range(14,15)))),
            },
        ]
    return render_template('orders.html', orders=orders)