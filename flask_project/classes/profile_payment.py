"""
Handle payment and billing address editing in profile
Should only be used for registered users
"""

from server import get_db, app
from flask_login import current_user

def get_default_payment_info(user_id=None):
    if not user_id:
        user_id = current_user.get_id()
    
    with app.app_context():
        db = get_db()
        user = db.get_entry_by_id("users", user_id)
        payment = db.get_entries_by_heading("payment", "user_id", user_id)
    
    if not user['is_authenticated']:
        return None

    return payment[0] if payment else None 
    
def get_default_billing_info(user_id=None):
    if not user_id:
        user_id = current_user.get_id()
    
    with app.app_context():
        db = get_db()
        user = db.get_entry_by_id("users", user_id)
        billing = db.get_entries_by_heading("billing", "user_id", user_id)

    if not user['is_authenticated']:
        return None
    
    return billing[0] if billing else None 

# set entries
def set_default_payment_info(name, number, expiry, cvc, user_id=None):
    if not user_id:
        user_id = current_user.get_id()

    with app.app_context():
        db = get_db()
        user = db.get_entry_by_id("users", user_id)
        payment_old = db.get_entries_by_heading("payment", "user_id", user_id)
    
    if not user or not user['is_authenticated']:
        return

    # Create entry for user
    if not payment_old:
        with app.app_context():
            db.add("payment", (user_id, name, number, expiry, cvc))
            return
    
    payment_old = payment_old[0] if payment_old else None

    # Update entry for user
    with app.app_context():
        payment_new = (payment_old['id'], user_id, name, number, expiry, cvc)
        db.update("payment", list(payment_old.values()), payment_new)

def set_default_billing_payment_info(address, country, state, zip_code, user_id=None):
    if not user_id:
        user_id = current_user.get_id()

    with app.app_context():
        db = get_db()
        user = db.get_entry_by_id("users", user_id)
        billing_old = db.get_entries_by_heading("billing", "user_id", user_id)
    
    if not user or not user['is_authenticated']:
        return
    
    billing_old = billing_old[0] if billing_old else None

    # Create entry for user
    if not billing_old:
        with app.app_context():
            db.add("billing", (user_id, address, country, state, zip_code))
            return
    
    # Update entry for user
    with app.app_context():
        billing_new = (billing_old['id'], user_id, address, country, state, zip_code)
        db.update("billing", list(billing_old.values()), billing_new)

# remove entries
def clear_default_payment_info(user_id=None):
    if not user_id:
        user_id = current_user.get_id()
    
    with app.app_context():
        db = get_db()
        user = db.get_entry_by_id("users", user_id)
        payment = db.get_entries_by_heading("payment", "user_id", user_id)
    
    if not user or not user['is_authenticated']:
        return False
    
    payment = payment[0] if payment else None
    if payment: 
        db.delete_by_id("payment", payment["id"])
        return True
    
    return False

def clear_default_billing_info(user_id=None):
    if not user_id:
        user_id = current_user.get_id()
    
    with app.app_context():
        db = get_db()
        user = db.get_entry_by_id("users", user_id)
        billing = db.get_entries_by_heading("billing", "user_id", user_id)
    
    if not user or not user['is_authenticated']:
        return False
    
    billing = billing[0] if billing else None
    if billing: 
        db.delete_by_id("billing", billing["id"])
        return True
    
    return False
    

