"""
Routes for a user's profile specific information
"""

from flask import redirect, request, render_template, url_for, jsonify, abort, session
from flask_login import current_user
from flask_login.utils import login_required

from server import app, get_db
from .endpoints import user_bp, api_bp
from .forms import UserProfileLoginSecurityForm, BillingAddressForm, CreditCardForm
from .forms import valid_states
from .forms import serialize_form

import datetime

from classes.cafepass import get_cafepass, CafepassInfo

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
    return render_template("profile/membership.html")

@api_bp.route('/profile/cafepass_add', methods=["POST"])
@login_required
def profile_cafepass_add():
    user_id = current_user.get_id()
    cafepass = get_cafepass(user_id)

    cafepass_old = list(cafepass.values())
    cafepass['level'] += 1
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
