
import sqlite3
from sqlite3 import dbapi2
import pandas as pd

class Table(object):
    def __init__(self, name, cols, conn, cur):
        self.name = name
        self.cols = cols
        self.conn = conn
        self.cur = cur

    def drop(self):
        try:
            self.cur.execute(f"DROP TABLE {self.name}")
        except Exception as e:
            print(e)

    def create(self):
        subquery1 = dict((i, self.cols[i]) for i in self.cols)
        subquery1 = ', '.join(f"{key} {val}" for (key,val) in subquery1.items())
        query = f"CREATE TABLE IF NOT EXISTS {self.name} ({subquery1})"
        self.cur.execute(query)
        print(f"table {self.name} created")


    # Fill table initially with some products from a xlsx file




    # Case insensitive, substring search
    def search_by_name(self, name):
        query = "SELECT * FROM product WHERE name LIKE ?"
        params = f"%{name}%",   # comma is intentional
        self.cur.execute(query, params)
        return [row for row in self.cur]

    def add(self, entry_no_id):
        # Assign a uid for the product
        cols_no_id = dict((i, self.cols[i]) for i in self.cols if i != "id")   # Drop rowid from entry class
        subquery1 = ', '.join(f"{key}" for key in cols_no_id.keys())
        subquery2 = ', '.join(f"?" for i in enumerate(cols_no_id))
        query = f"INSERT INTO {self.name} ({subquery1}) VALUES ({subquery2})"
        params = entry_no_id
        print(query, params)
        self.cur.execute(query, params)
        self.conn.commit()
        print(f"Entry {entry_no_id[0]} added")
        
    def delete(self, entry):
        query = f"DELETE FROM {self.name} WHERE rowid = ?"
        params = int(entry[0]), # comma is intentional
        self.cur.execute(query, params)
        self.conn.commit()
        print(f"Entry {entry[0]} deleted")

    def update(self, entry_old, entry_new):
        subquery1 = ', '.join(f"{col} = ?" for (i, col) in enumerate(self.cols))
        query = f"UPDATE {self.name} SET {subquery1} WHERE id = {entry_old[0]}"
        params = entry_new
        print(query)
        print(params)
        self.cur.execute(query, params)
        self.conn.commit()
        print(f"Entry {entry_new[0]} updated")

