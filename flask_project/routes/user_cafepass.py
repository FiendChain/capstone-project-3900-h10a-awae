"""
Routes for a user's profile specific information
"""

from flask import json, redirect, request, render_template, url_for, jsonify, abort, session
from flask_login import current_user
from flask_login.utils import login_required

from server import app, get_db
from .endpoints import user_bp, api_bp
from .forms import CafePassForm, serialize_form, PaymentCardForm, valid_states

import datetime

from classes.cafepass import get_cafepass, CafepassInfo
from classes.profile_payment import get_default_billing_info, get_default_payment_info

@app.before_request
def create_cafepass():
    if not current_user.is_authenticated:
        return

    user_id = current_user.get_id() 
    cafepass = get_cafepass(user_id)
    if cafepass is not None:
        return
    
    print(f"Creating cafepass for user: {user_id}")
    with app.app_context():
        db = get_db()
        db.add("cafepass", (user_id, 0, 0, 1))

@user_bp.route('/profile/membership')
@login_required
def profile_membership():
    user_id = current_user.get_id()
    cafepass = get_cafepass(user_id)

    cafepass_form = CafePassForm()
    form = PaymentCardForm()
    cafepass_form.paid.data = bool(cafepass['paid'])

    default_billing_info = get_default_billing_info()
    info = get_default_payment_info()
    default_payment_info = info and dict(
        cc_name=info["name"],
        cc_number=info["number"],
        cc_expiry=info["expiry"],
        cc_cvc=info["cvc"] 
    )

    data = dict(
        form=form,  # payment and billing form
        cafepass_form=cafepass_form,
        default_billing_info=default_billing_info,
        default_payment_info=default_payment_info,
        valid_states=valid_states
    )
    return render_template("profile/membership.html", **data)

@api_bp.route('/profile/membership', methods=["POST"])
@login_required
def profile_membership():
    print("BATTLEP[ASS BOUGHT")
    form = CafePassForm()
    if not form.validate_on_submit():
        return redirect(url_for("user_bp.profile_membership"))

    user_id = current_user.get_id()
    cafepass = get_cafepass(user_id)
    cafepass_old = list(cafepass.values())
    # cafepass['paid'] = int(form.paid.data)
    cafepass['paid'] = 1
    cafepass_new = list(cafepass.values())

    with app.app_context():
        db = get_db()
        db.update("cafepass", cafepass_old, cafepass_new)
    
    return redirect(url_for("user_bp.profile_membership"))

@app.context_processor
def battlepass_injector():
    cafepass = get_cafepass(current_user.get_id())
    if cafepass:
        with app.app_context():
            db = get_db()
        cafepass = CafepassInfo(cafepass, db)
    return dict(current_cafepass=cafepass)
