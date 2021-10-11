from flask import Flask, json, redirect, request, render_template, url_for, send_from_directory, jsonify
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask import g
from flask import Blueprint

# @app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        if db.conn is not None:
            db.conn.close()

# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_db', None)
#     if db is not None:
#         db.close()