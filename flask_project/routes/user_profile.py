"""
Routes for a user's profile specific information
"""

from re import S
from flask import redirect, request, render_template, url_for, jsonify, abort, session
from flask_login import current_user
from flask_login.utils import login_required

from server import app, get_db
from .endpoints import user_bp, api_bp
from .forms import UserProfileLoginSecurityForm, BillingAddressForm, CreditCardForm
from .forms import valid_states
from .forms import serialize_form

from classes.profile_payment import get_default_payment_info, get_default_billing_info
from classes.profile_payment import set_default_payment_info, set_default_billing_payment_info

import datetime

# User account
@user_bp.route('/profile', methods=["GET"])
def profile():
    return render_template("profile.html")

@user_bp.route('/profile/login_security', methods=["GET"])
@login_required
def profile_edit_login_security():
    form = UserProfileLoginSecurityForm()
    id = current_user.get_id()
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
        id = current_user.get_id()
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
        return jsonify(dict(redirect=url_for("user_bp.profile"))), 200
    return jsonify(serialize_form(form)), 400

# Address information
@user_bp.route('/profile/address')
@login_required
def profile_address():
    form = BillingAddressForm(data=get_default_billing_info())
    return render_template("profile/address.html", form=form, valid_states=valid_states)

@api_bp.route("/profile/address", methods=["POST"])
@login_required
def profile_address():
    form = BillingAddressForm()
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 400
    
    set_default_billing_payment_info(
        form.address.data, form.country.data, 
        form.state.data, form.zip_code.data)

    return jsonify(dict(redirect=url_for("user_bp.profile_address"))), 200

# Payment information
@user_bp.route('/profile/payment')
@login_required
def profile_payment():
    data = get_default_payment_info()
    data = data and dict(
        cc_name=data["name"],
        cc_number=data["number"],
        cc_expiry=data["expiry"],
        cc_cvc=data["cvc"],
    )

    form = CreditCardForm(data=data)
    return render_template("profile/payment.html", form=form)

@api_bp.route("/profile/payment", methods=["POST"])
@login_required
def profile_payment():
    form = CreditCardForm()
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 400
    
    set_default_payment_info(
        form.cc_name.data, form.cc_number.data,
        form.cc_expiry.data, form.cc_cvc.data)

    return jsonify(dict(redirect=url_for("user_bp.profile_payment"))), 200

