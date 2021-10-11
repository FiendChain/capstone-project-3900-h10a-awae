# %%
from flask import Flask
from flask_login import LoginManager
import sqlite3
import pandas as pd
from classes.table import *
from classes.database import *
import os
from flask import g

<<<<<<< HEAD
app = Flask(__name__)
print("System setting up...")
=======
app = Flask(__name__, static_folder='static', static_url_path='/static')
>>>>>>> wy_frontend

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = Database("db/ecommerce.db")
    return db
    

# Flask setup
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = 'very-secret-123' # must include

<<<<<<< HEAD
# System setup
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
    x = db.search_product_by_name("tall coffee")
    print(x)
    db.conn.close()
print("System finished setting up")
# table_products = Table("products", table_cols["products"], conn, cur)
# table_accounts = Table("accounts", table_cols["accounts"], conn, cur)

# table_products.drop()
# table_products.create()
# file_path = os.path.abspath(os.getcwd())+"\lmao.db"
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path
# db = SQLAlchemy(app)
# db.create_all()
# # %%
# path_products = "data/awae_products.xlsx"
# df = pd.read_excel(path_products, engine = 'openpyxl')
# entries = df.to_numpy().tolist()
# for entry in entries:

# db.session.add_all()
=======
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
        x = db.search_product_by_name("tall coffee")
        print(x)
        db.conn.close()
    print("System finished setting up")
    # table_products = Table("products", table_cols["products"], conn, cur)
    # table_accounts = Table("accounts", table_cols["accounts"], conn, cur)

    # table_products.drop()
    # table_products.create()

create_database()
>>>>>>> wy_frontend
