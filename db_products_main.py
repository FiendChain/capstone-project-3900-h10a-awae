# %%
import sqlite3
import pandas as pd
from table import *
from database import *


# Create table
table_name = "products"
table_cols = {
    "products": {
        "id": "INTEGER PRIMARY KEY NOT NULL",
        "name": "text NOT NULL",
        "price": "real NOT NULL",
        "brand": "text",
        "category": "text",
        "description": "text",
        "delivery": "int",
        "warranty": "real",
        "image_link": "text"
    },
    "accounts": {
        "id": "INTEGER PRIMARY KEY NOT NULL",
        "username": "text NOT NULL",
        "password": "text NOT NULL",
        "email": "text NOT NULL",
        "first_name": "text NOT NULL",
        "last_name": "text NOT NULL",
        "dob": "text NOT NULL",
        "is_admin": "int NOT NULL"
    }
}

# Create product DB and fill it with products
db = Database()
conn, cur = db.connect()
table_products = Table("products", table_cols["products"], conn, cur)
table_accounts = Table("accounts", table_cols["accounts"], conn, cur)

table_products.drop()
table_products.create()
table_accounts.drop()
table_accounts.create()

table_products.fill(db.path_products)
table_accounts.fill(db.path_accounts)   # Account dob does not work yet
#print(search_products_by_name(cur, "")) # List all products
# %%
# Add new product
product_no_id = ("Sample coffee product", "4.99", "Sample brand", "Sample category", "Sample description", "8", "2", "Sample source")
# uid = get_next_uid(cur, table_name)
# product = (uid,) + product
table_products.add(product_no_id)
# print(search_products_by_name(cur, "sample"))
# %%
# Edit existing product
product_old = table_products.search_by_name("Sample coffee product")[-1]
# We pass entry_old to frontend, and it will return entry_new with updated product values, with the old id too
product_new = list(product_old)
product_new[1] = "edited sample coffee product"
product_new[5] = "edited sample description"

product_new = tuple(product_new)    # Entry must be tuple format
table_products.update(product_old, product_new)
# print(search_products_by_name(cur, "sample"))

# %%
# Delete product
product = table_products.search_by_name("Sample coffee product")[-1]
table_products.delete(product)
print(table_products.search_by_name("sample"))
# %%
db.close(db)
# %%
