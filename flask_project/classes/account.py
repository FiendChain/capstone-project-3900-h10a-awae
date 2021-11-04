from server import login_manager, app, get_db
from .flaskuser import FlaskUser

import uuid

def get_flask_user_from_db(user):
    flask_user = FlaskUser(
        user["username"], user["is_authenticated"], 
        True, False, 
        user["id"], user["is_admin"]) 

    return flask_user


def get_login_user(username, password):
    with app.app_context():
        db = get_db()
    
    if not db.validate_user(username, password):
        return None
    
    user = db.get_entries_by_heading("users", "username", username)[0]
    flask_user = get_flask_user_from_db(user)
    return flask_user

class UsernameTaken(Exception):
    def __init__(self, username):
        self.username = username
        super().__init__(f"Username '{username}' is taken")

def create_registered_user(username, password, email, phone):
    with app.app_context():
        db = get_db()

    is_admin = 0 
    is_authenticated = 1
    user_data = (username, password, email, phone, is_admin, is_authenticated)

    try:
        db.add("users", user_data)
    except Exception:
        raise UsernameTaken(username)

    user = db.get_entries_by_heading("users", "username", username)[0]
    flask_user = get_flask_user_from_db(user)

    return flask_user

def get_guest_account(guest_id):
    with app.app_context():
        db = get_db()
    
    user = db.get_entry_by_id("users", guest_id)

    # if not a guest user, don't login
    if user is None or user['is_authenticated']:
        return None
    
    flask_user = get_flask_user_from_db(user)
    return flask_user
    
def create_guest_account():
    with app.app_context():
        db = get_db()

    while True:
        id = str(uuid.uuid4())

        username = f"Guest#{id}"
        password = ""
        email = ""
        phone = ""
        is_admin = 0
        is_authenticated = 0

        user_data = (username, password, email, phone, is_admin, is_authenticated)

        try:
            db.add("users", user_data)
        except Exception as ex:
            continue

        break

    user = db.get_entries_by_heading("users", "username", username)[0]
    flask_user = get_flask_user_from_db(user)
    return flask_user
