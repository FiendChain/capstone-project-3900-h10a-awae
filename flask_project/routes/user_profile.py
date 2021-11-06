"""
Routes for a user's profile specific information
"""

from re import S
from flask import redirect, request, render_template, url_for, jsonify, abort, session, flash
from flask_login import current_user
from flask_login.utils import login_required

from server import app, get_db
from .endpoints import user_bp, api_bp
from .forms import UserProfileLoginSecurityForm, BillingAddressForm, CreditCardForm
from .forms import valid_states
from .forms import serialize_form, api_redirect

from classes.profile_payment import get_default_payment_info, get_default_billing_info
from classes.profile_payment import set_default_payment_info, set_default_billing_payment_info
from classes.profile_payment import clear_default_payment_info, clear_default_billing_info

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
    if not form.validate_on_submit():
        return jsonify(serialize_form(form)), 400

    with app.app_context():
        db = get_db()

    user_id = current_user.get_id()
    user = db.get_entry_by_id("users", user_id)

    if not db.validate_user(user["username"], form.password.data): # If entered password does not match password in database, return error
        form.password.errors.append("Incorrect password")
        return jsonify(serialize_form(form)), 400

    user_old = list(user.values())
    user['password'] = form.new_password.data
    user['email'] = form.email.data
    user['phone'] = form.phone.data
    user_new = list(user.values())
    db.update("users", user_old, user_new)

    flash("Successfully updated login details")
    return api_redirect(url_for("user_bp.profile"))

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

    flash("Successfully updated billing details")
    return api_redirect(url_for("user_bp.profile_address"))

@api_bp.route("/profile/clear_address", methods=["POST"])
@login_required
def clear_profile_address():
    clear_default_billing_info()
    flash("Successfully cleared billing details")
    return redirect(url_for('user_bp.profile_address'))

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

    flash("Successfully updated payment details")
    return api_redirect(url_for("user_bp.profile_payment"))

@api_bp.route("/profile/clear_payment", methods=["POST"])
@login_required
def clear_profile_payment():
    clear_default_payment_info()
    flash("Successfully cleared payment details")
    return redirect(url_for('user_bp.profile_payment'))
