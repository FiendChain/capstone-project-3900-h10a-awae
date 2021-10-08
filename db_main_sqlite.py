# %%
import sqlite3
import pandas as pd

def db_connect(path_db):
    db = sqlite3.connect(path_db)
    cur = db.cursor()
    return db, cur

def table_drop(cur, table_name):
    try:
        cur.execute(f"DROP TABLE {table_name}")
    except Exception as e:
        print(e)

def table_create(cur, table_name, identifiers):
    # OK to use fstrings in this query because query is initiated by the system, not user
    query = f"CREATE TABLE {table_name} ({identifiers})"
    cur.execute(query)
    print("table products created")

def table_fill(db, cur, table_name, path_products):
    df_coffee = pd.read_excel(path_products, engine = 'openpyxl')
    products = df_coffee.to_numpy().tolist()
    query = f"INSERT INTO {table_name} VALUES ({wildcards[table_name]})"
    params = products
    cur.executemany(query, params)
    db.commit()
    print("Sample products filled")

def db_close(db):
    db.close()
    print("db closed")

# Case insensitive, substring search
def search_products_by_name(cur, name):
    query = '''SELECT * FROM products WHERE name LIKE ?'''
    params = f"%{name}%",   # comma is intentional
    cur.execute(query, params)
    return [row for row in cur]


# Find highest uid in the table, add one, and return
def get_next_uid(cur, table_name):
    # OK to use fstring here because table_name is generated from the system and not user
    query = f"SELECT uid FROM {table_name} ORDER BY uid desc LIMIT 1"
    cur.execute(query)
    return cur.fetchone()[0] + 1


def table_add(db, cur, table_name, wildcard, entry):
    # Assign a uid for the product

    query = f"INSERT INTO {table_name} VALUES ({wildcard})"
    params = entry
    cur.execute(query, params)
    db.commit()
    print(f"Entry {entry[0]} added")
    
def table_delete(db, cur, table_name, entry):
    query = f"DELETE FROM {table_name} WHERE uid=?"
    params = int(entry[0]), # comma is intentional
    cur.execute(query, params)
    db.commit()
    print(f"Entry {entry[0]} deleted")

def table_update(db, cur, table_name, wildcard, entry_old, entry_new):
    # Updating all rows in an entry is easier by deleting and adding, than using update 
    table_delete(db, cur, table_name, entry_old)
    table_add(db, cur, table_name, wildcard, entry_new)
    print(f"Entry {entry_new[0]} updated")


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
table_fill(db, cur, table_name, path_products)
#print(search_products_by_name(cur, "")) # List all products
# %%
# Add new product
product = ("Sample coffee product", "4.99", "Sample brand", "Sample category", "Sample description", "8", "2", "Sample source")
uid = get_next_uid(cur, table_name) # A uid must be generated and appended to the product before it can be added
product = (uid,) + product
table_add(db, cur, table_name, wildcards[table_name], product)
print(search_products_by_name(cur, "sample"))
# %%
# Edit existing product
product_old = search_products_by_name(cur, "Sample coffee product")[-1]
# We pass entry_old to frontend, and it will return entry_new with updated product values
product_new = list(product_old)
product_new[1] = "UPDATED sample coffee product"
product_new[5] = "UPDATED sample description"

product_new = tuple(product_new)    # Entry must be tuple format
table_update(db, cur, table_name, wildcards[table_name], product_old, product_new)
print(search_products_by_name(cur, "sample"))

# %%
# Delete product
product = search_products_by_name(cur, "Sample coffee product")[-1]
table_delete(db, cur, table_name, product)
print(search_products_by_name(cur, "sample"))
# %%
db_close(db)
# %%
