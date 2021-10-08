# %%
import sqlite3
import pandas as pd
from db_helpers import *

table_identifiers = {
    "products": "uid int, name text, price real, brand text, category text, description text, delivery int, warranty real, image_link text"
}

path_db = "db_sqlite/ecommerce.db"
path_products = "data/awae_products.xlsx"

# To prevent SQL injection and for better database security, we must use wildcards instead of variable names in the query
wildcards = {
    "products": "?, ?, ?, ?, ?, ?, ?, ?, ?",
    "accounts": "?, ?, ?, ?, ?"
}
table_name = "products"

# Create product DB and fill it with products
db, cur = db_connect(path_db)
table_drop(cur, table_name)
table_create(cur, table_name, table_identifiers[table_name])
table_fill(db, cur, table_name, wildcards[table_name], path_products)
#print(search_products_by_name(cur, "")) # List all products
# %%
# Add new product
product = ("Sample coffee product", "4.99", "Sample brand", "Sample category", "Sample description", "8", "2", "Sample source")
uid = get_next_uid(cur, table_name) # A uid must be generated and appended to the product before it can be added
product = (uid,) + product
table_add(db, cur, table_name, wildcards[table_name], product)
# print(search_products_by_name(cur, "sample"))
# %%
# Edit existing product
product_old = search_products_by_name(cur, "Sample coffee product")[-1]
# We pass entry_old to frontend, and it will return entry_new with updated product values
product_new = list(product_old)
product_new[1] = "UPDATED sample coffee product"
product_new[5] = "UPDATED sample description"

product_new = tuple(product_new)    # Entry must be tuple format
table_update(db, cur, table_name, wildcards[table_name], product_old, product_new)
# print(search_products_by_name(cur, "sample"))

# %%
# Delete product
product = search_products_by_name(cur, "Sample coffee product")[-1]
table_delete(db, cur, table_name, product)
print(search_products_by_name(cur, "sample"))
# %%
db_close(db)
# %%
