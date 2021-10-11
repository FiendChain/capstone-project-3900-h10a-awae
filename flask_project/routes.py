# Store all routes here

from flask import Flask, redirect, request, render_template, url_for
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from server import app, login_manager
from flask import g

    
# The first page displayed upon startup
@app.route('/', methods = ["GET", "POST"])
def login():
    somedata = "passing in some post data"
    return render_template("homepage.html", somedata = somedata)


# Reloads and returns the User object for current session
@login_manager.user_loader
def load_user(name):
    pass


# The home page
@app.route('/index')
@login_required
def index():
    pass

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        if db.conn is not None:
            db.conn.close()

