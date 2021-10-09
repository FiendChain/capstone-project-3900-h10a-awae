# %%
# DB parameters
import sqlite3
import pandas as pd
class Database(object):
    def __init__(self, path):
        self.path = path
        self.tables = {}
        print(self.path)
        conn = sqlite3.connect(self.path)
        cur = conn.cursor()
        self.conn = conn
        self.cur = cur
        print("db connected, use db.conn and db.cur")
    
    def tables_create(self, f):
        self.cur.executescript(f.read()) # Read sql schema and create tables
        self.conn.commit()

        # cur = db.conn.execute("select * from product")
        # names = [description[0] for description in cur.description]
        table_names = self.get_table_names()
        for table_name in table_names:
            table_headings = self.get_table_headings(table_name)
            self.tables[table_name] = table_headings

    def get_table_names(self):
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = [value[0] for idx, value in enumerate(self.cur.fetchall())]
        return table_names

    def get_table_headings(self, table_name):
        self.cur.execute(f"select * from {table_name}")
        table_headings = [description[0] for description in self.cur.description]
        return table_headings

    def fill(self, table_name, path_products):
        df = pd.read_excel(path_products, engine = 'openpyxl')
        entries = df.to_numpy().tolist()
        cols_no_id = dict((i, self.cols[i]) for i in self.cols if i != "id")
        subquery_1 = ', '.join(f"{key}" for key in cols_no_id.keys())
        subquery_2 = ', '.join(f"?" for (i, col) in enumerate(cols_no_id))
        query = f"INSERT INTO {table_name} ({subquery_1}) VALUES ({subquery_2})"
        print(query)
        print(entries)
        params = entries
        self.cur.executemany(query, params)
        self.conn.commit()
        print("Sample entries filled")
    


    def drop(self, table):
        try:
            self.cur.execute(f"DROP TABLE {table}")
        except Exception as e:
            print(e)

    # def create(self):
    #     subquery1 = dict((i, self.cols[i]) for i in self.cols)
    #     subquery1 = ', '.join(f"{key} {val}" for (key,val) in subquery1.items())
    #     query = f"CREATE TABLE IF NOT EXISTS {self.name} ({subquery1})"
    #     self.cur.execute(query)
    #     print(f"table {self.name} created")


    # Fill table initially with some products from a xlsx file




    # Case insensitive, substring search
    def search_by_name(self, name):
        query = "SELECT * FROM products WHERE name LIKE ?"
        params = f"%{name}%",   # comma is intentional
        self.cur.execute(query, params)
        return [row for row in self.cur]

    def add(self, table_name, entry_no_id):
        # Assign a uid for the product
        cols_no_id = dict((i, self.cols[i]) for i in self.cols if i != "id")   # Drop rowid from entry class
        subquery1 = ', '.join(f"{key}" for key in cols_no_id.keys())
        subquery2 = ', '.join(f"?" for i in enumerate(cols_no_id))
        query = f"INSERT INTO {table_name} ({subquery1}) VALUES ({subquery2})"
        params = entry_no_id
        print(query, params)
        self.cur.execute(query, params)
        self.conn.commit()
        print(f"Entry {entry_no_id[0]} added")
        
    def delete(self, table_name, entry):
        query = f"DELETE FROM {table_name} WHERE rowid = ?"
        params = int(entry[0]), # comma is intentional
        self.cur.execute(query, params)
        self.conn.commit()
        print(f"Entry {entry[0]} deleted")

    def update(self, table_name, entry_old, entry_new):
        subquery1 = ', '.join(f"{col} = ?" for (i, col) in enumerate(self.cols))
        query = f"UPDATE {table_name} SET {subquery1} WHERE id = {entry_old[0]}"
        params = entry_new
        print(query)
        print(params)
        self.cur.execute(query, params)
        self.conn.commit()
        print(f"Entry {entry_new[0]} updated")




# # To prevent SQL injection and for better database security, we must use wildcards instead of variable names in the query
# wildcards = {
#     "products": "?, ?, ?, ?, ?, ?, ?, ?",
#     "accounts": "?, ?, ?, ?, ?, ?, ?"
# }