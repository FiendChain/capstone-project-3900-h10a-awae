# %%
import os
import sys
print(os.path.abspath(''))
from pymongo import MongoClient
import pandas as pd
from db_helpers import *



# Initialize DB and collections
port = "12345"
db = init_db(port)
collection_products = init_collection_products(db)
collection_accounts = init_collection_accounts(db)

# Insert some sample data
sample_products_csv = "data/products_sample.csv"
sample_accounts_csv = "data/accounts_sample.csv"
insert_sample_products(sample_products_csv, collection_products)
insert_sample_accounts(sample_accounts_csv, collection_accounts)

# Print entries in collections
print([x for x in collection_products.find()])
print([x for x in collection_accounts.find()])




# %%
# Retrieve existing product(s) in DB by name
# Works with any substring and is case-insensitive
product_name = "lat wh"
items = search_products(product_name, collection_products)
print(*items, sep = "\n")
# %%
# Add new product to product database
product_new = {
    "price": 30.95,
    "category": "CAT1",
    "description": "Updated product!!!",
    "delivery": 10,
    "stock": 4001
}
try:
    add_product(product_new, collection_products)
except Exception as e:
    print("ERROR adding product:\n", e)
# %%
# Update existing product in database
product_name = "americano"
items = search_products("americano", collection_products)
print("Old products:")
print(*items, sep = "\n")
product_old = items[0]

# Values for each attribute will be passed in from frontend
# Product ID must still remain same as old one and non-editable
product_new = {
    "_id": product_old["_id"],
    "price": 30.95,
    "category": "CAT1",
    "description": "Updated product!!!",
    "delivery": 10,
    "stock": 4001
}
try:
    update_product(product_old, product_new, collection_products)
    items = search_products("americano", collection_products)
    print("Updated products:")
    print(*items, sep = "\n")
except Exception as e:
    print("ERROR updating product:\n", e)
# %%
# Delete one or more products
product_name = "tea"
items = search_products(product_name, collection_products)
print(*items, sep = "\n")

# Frontend will pass down what product is to be removed
products1 = items[-1]
products2 = items[0:-1]

try:
    delete_products(products1, collection_products)  # Delete 1 product
    items = search_products("tea", collection_products)
    print(*items, sep = "\n")
    delete_products(products2, collection_products) # Delete many products
    items = search_products("tea", collection_products)
    print(*items, sep = "\n")
except Exception as e:
    print("ERROR deleting product:\n", e)

# %%
# Add new account
account_new = {
    "username": "hello",
    "password": "world",
    "first_name": "Will",
    "last_name": "Smith",
    "dob": "20/6/1970"
}
add_account(account_new, collection_accounts)
items = search_accounts("", collection_accounts)
print(items)
# %%
