# Store all routes here

from flask import Flask, json, redirect, request, render_template, url_for, send_from_directory, jsonify
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask import g
from flask import Blueprint

from server import login_manager

admin_bp = Blueprint('admin_bp', __name__, static_folder='static', static_url_path='/static', template_folder='templates')


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("admin/login.html")
    
    return redirect(url_for("admin_bp.home"))

@admin_bp.route('/', methods=['GET'])
def home():
    return render_template("admin/home.html")
