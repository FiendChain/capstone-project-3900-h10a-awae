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

# update level after a purchase 
def refresh_level(db, info):
    net_xp = info['net_xp']
    curr_level = 0
    for i in range(1, 20):
        level = db.get_entries_by_heading("level", "level", i)
        if not level:
            break
        level = level[0]
        level_xp = level['xp']

        if level_xp > net_xp:
            break

        curr_level = i
    
    if curr_level != info['level']:
        info_old = info.values()
        info['level'] = curr_level
        info_new = info.values()
        db.update("cafepass", info_old, info_new)
        return True
    return False

class CafepassInfo:
    def __init__(self, info, db):
        self.level = info['level']
        self.id = info['id']
        self.user_id = info['user_id']
        self.paid = info['paid']
        self.net_xp = info['net_xp']

        assert self.level > 0

        curr_level = db.get_entries_by_heading("level", "level", self.level)
        prev_level = db.get_entries_by_heading("level", "level", self.level-1)

        curr_level = curr_level[0] if curr_level else None
        prev_level = prev_level[0] if prev_level else None

        assert curr_level
        assert prev_level

        self.curr_level_info = curr_level
        self.prev_level_info = prev_level
    
    @property
    def frac_complete(self):
        remaining_xp = self.remaining_xp
        if remaining_xp == 0:
            return 1

        delta = self.curr_level_info['xp']-self.prev_level_info['xp']
        return self.net_xp / delta
    
    @property
    def percent_complete(self):
        return self.frac_complete * 100
    
    @property
    def percent_discount(self):
        if self.paid:
            return self.curr_level_info['discount_paid']
        return self.curr_level_info['discount_free']

    # Calculate total xp till next level
    @property
    def remaining_xp(self):
        return self.curr_level_info['xp']-self.net_xp
    
    @property
    def curr_milestone(self):
        return self.curr_level_info['xp']
    
    @property
    def prev_milestone(self):
        return self.prev_level_info and self.prev_level_info['xp']
    
def get_cafepass(user_id):
    with app.app_context():
        db = get_db()
        cafepass = db.get_entries_by_heading("cafepass", "user_id", user_id)

    if cafepass:
        cafepass = cafepass[0]
    else:
        cafepass = None

    return cafepass

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
        db.add("cafepass", (user_id, 0, 0, 0))

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

    print(cafepass)

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
