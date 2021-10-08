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

def table_fill(db, cur, table_name, wildcard, path_products):
    df_coffee = pd.read_excel(path_products, engine = 'openpyxl')
    products = df_coffee.to_numpy().tolist()
    query = f"INSERT INTO {table_name} VALUES ({wildcard})"
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

