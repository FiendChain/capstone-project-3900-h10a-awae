# %%
from pymongo import MongoClient
import pandas as pd



# client = pymongo.MongoClient("mongodb+srv://admin:admin@ecommerce.atmzr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
client = MongoClient("mongodb://localhost:12345/")

print("Creating ecommerce db...")

if "ecommerce" in client.list_database_names():
    print("Existing ecommerce db found, dropping...")
    client.drop_database("ecommerce")
    print("Existing ecommerce db dropped.")

db = client["ecommerce"]    # Connect to ecommerce database
print("Ecommerce db created")

# %%
# Create database of products
collection_products = db["products"]
df_coffee = pd.read_csv("data/products_sample.csv")
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
for x in collection_products.find():
    print(x)

# Create database of accounts
collection_accounts = db["accounts"]
df_accounts = pd.read_csv("data/accounts_sample.csv")
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
for x in collection_accounts.find():
    print(x)
# %%
