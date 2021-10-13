from functools import wraps
from flask import current_app, flash
from flask_login.utils import login_required
from flask_login import current_user

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin:
            flash("Administrative permissions required")
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    authenticated_view = login_required(decorated_view)
    return authenticated_view