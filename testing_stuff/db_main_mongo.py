# %%
#import os
#import sys
#print(os.path.abspath(''))
from pymongo import MongoClient
import pandas as pd
#from db_helpers import *

from pymongo import MongoClient
import pandas as pd

def init_db(port):
    print("Creating ecommerce db...")
    # Local DB
    client = MongoClient(f"mongodb://localhost:{port}/")
    # Online DB
    # client = pymongo.MongoClient("mongodb+srv://admin:admin@ecommerce.atmzr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    if "ecommerce" in client.list_database_names():
        print("Existing ecommerce db found, dropping...")
        client.drop_database("ecommerce")
        print("Existing ecommerce db dropped.")
    db = client["ecommerce"]    # Connect to ecommerce database
    print("Ecommerce db created")
    return db

def init_collection_products(db):
    collection_products = db["products"]
    return collection_products

def insert_sample_products(sample_products_csv, collection_products):
    df_coffee = pd.read_csv(sample_products_csv)
    products = []
    for index, row in df_coffee.iterrows():
        product = {
            "name": row["name"],
            "price": row["price"],
            "category": row["category"],
            "description": row["description"],
            "delivery": row["delivery"],
            "stock": row["stock"]
        }
        products.append(product)
    collection_products.insert_many(products)

def init_collection_accounts(db):
    collection_accounts = db["accounts"]
    return collection_accounts

def insert_sample_accounts(sample_accounts_csv, collection_accounts):
    df_accounts = pd.read_csv(sample_accounts_csv)
    accounts = []
    for index, row in df_accounts.iterrows():
        account = {
            "username": row["username"],
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "dob": row["dob"]
        }
        accounts.append(account)
    collection_accounts.insert_many(accounts)

def search_products(product_name, collection_products):
    items = [x for x in collection_products.find({"name": {"$regex": f'{product_name}', "$options": "$i"}})]
    return items

def add_product(product_new, collection_products):
    collection_products.insert_one(product_new)

def update_product(product_old, product_new, collection_products):
    collection_products.update_one({"_id": product_old["_id"]}, {"$set": product_new})

def delete_products(products, collection_products):
    if not isinstance(products, list):
        products = [products]
    for product in products:
        collection_products.delete_one({"_id": product["_id"]})


def search_accounts(account_name, collection_accounts):
    items = [x for x in collection_accounts.find({"name": {"$regex": f'{account_name}', "$options": "$i"}})]
    return items

def add_account(account_new, collection_accounts):
    collection_accounts.insert_one(account_new)

def update_account(account_old, account_new, collection_account):
    collection_account.update_one({"_id": account_old["_id"]}, {"$set": account_new})

def delete_accounts(accounts, collection_accounts):
    if not isinstance(accounts, list):
        accounts = [accounts]
    for account in accounts:
        collection_accounts.delete_one({"_id": account["_id"]})


# Initialize DB and collections
port = "12345"
db = init_db(port)
collection_products = init_collection_products(db)
collection_accounts = init_collection_accounts(db)

# Insert some sample data
sample_products_csv = "/data/products_sample.csv"
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
