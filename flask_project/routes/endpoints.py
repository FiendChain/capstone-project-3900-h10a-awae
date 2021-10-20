from flask import Blueprint

admin_bp = Blueprint('admin_bp', __name__, static_folder='static', static_url_path='/static', template_folder='templates')
admin_api_bp = Blueprint('admin_api_bp', __name__, static_folder='static', static_url_path='/static', template_folder='templates')
user_bp  = Blueprint('user_bp', __name__, static_folder='static', static_url_path='/static', template_folder='templates')
api_bp = Blueprint('api_bp', __name__)


