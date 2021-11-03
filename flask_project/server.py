# %%
from flask import Flask, Blueprint
from flask_login import LoginManager
import sqlite3
import pandas as pd
from classes.table import *
from classes.database import *
import os
from flask import g

import os
import pathlib

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__, static_folder='static', static_url_path='/static')

# setup path for saving uploaded files
upload_folder = os.path.join(app.instance_path, '../static/uploads')
image_folder = os.path.join(upload_folder, 'images')
pathlib.Path(image_folder).mkdir(exist_ok=True, parents=True)
print(f"Setting upload image path: {image_folder}")

app.config['UPLOADED_IMAGES_DEST'] = image_folder

app.secret_key = 'very-secret-123' # must include

login_manager = LoginManager()
login_manager.login_view = "user_bp.login"

# generate database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = Database("db/ecommerce.db")
    return db

# Create product DB and fill it with products
def create_database():
    # System setup
    print("System setup")
    # Create table
    table_name = "products"

    def make_dicts(cursor, row):
        return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))

    # db = Database("db/ecommerce.db")# Save db in application context
    if os.path.exists("db/ecommerce.db"):
        os.remove("db/ecommerce.db")

    with app.app_context():
        db = get_db()   # Initialize db
        db.drop
        with app.open_resource('db/ecommerce.sql', mode='r') as f:
            db.tables_create(f)
        # print(db.tables)

        db.fill("products", "data/awae_products.xlsx")
        db.fill("users", "data/awae_accounts.xlsx")
        db.fill("level", "data/awae_levels.xlsx")
        db.fill("payment", "data/awae_default_payment.xlsx")
        db.fill("billing", "data/awae_default_billing.xlsx")
        # db.add("users", (
        #     "Arnold", "Schwar", "arnold@gmail.com", "0404123456", 0
        # ))
        # print(db.get_unique_values("products", "category"))
        # print(db.search_product_by_name("", category = "Meal Kit", order_by = "unit_price ASC"))
        db.conn.close()
    print("System finished setting up")
    # table_products = Table("products", table_cols["products"], conn, cur)
    # table_accounts = Table("accounts", table_cols["accounts"], conn, cur)

    # table_products.drop()
    # table_products.create()

create_database()

