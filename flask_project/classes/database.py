# %%
# DB parameters
import sqlite3
import pandas as pd
class Database(object):
    def __init__(self, path):
        self.path = path
        self.tables = {}
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

    def fill(self, table_name, path_excel):
        df = pd.read_excel(path_excel, engine = 'openpyxl')
        entries = df.to_numpy().tolist()
        cols_no_id = [x for x in self.tables[table_name] if x != "id"]
        subquery_1 = ', '.join(f"{key}" for key in cols_no_id)
        subquery_2 = ', '.join(f"?" for (i, col) in enumerate(cols_no_id))
        query = f"INSERT INTO {table_name} ({subquery_1}) VALUES ({subquery_2})"
        params = entries
        self.cur.executemany(query, params)
        self.conn.commit()
        print(f"Sample {table_name} filled")
    

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

    # Case insensitive, substring search
        # sort_filter: price    
    # sort_order: asc, desc

    def search_product_by_name(self, name="", category = "", order_by="id ASC"):
        query = f"SELECT * FROM products WHERE name LIKE ? AND category = {category} ORDER BY {order_by}"
        params = f"%{name}%",   # comma is intentional
        self.cur.execute(query, params)
        entries = self.cur.fetchall()
        entries = [self.make_dict(self.cur, entry) for entry in entries]
        return entries

    def add(self, table_name, entry_no_id):
        # Assign a uid for the product
        cols = self.get_table_headings(table_name)
        cols_no_id = [col for col in cols if col != "id"]   # Drop rowid from entry class
        
        subquery1 = ', '.join(f"{col}" for col in cols_no_id)
        subquery2 = ', '.join(f"?" for i in enumerate(cols_no_id))
        query = f"INSERT INTO {table_name} ({subquery1}) VALUES ({subquery2})"
        params = entry_no_id
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
        cols = self.get_table_headings(table_name)
        #cols_no_id = [col for col in cols if col != "id"]   # Drop rowid from entry class

        
        subquery1 = ', '.join(f"{col} = ?" for col in cols)
        query = f"UPDATE or IGNORE {table_name} SET {subquery1} WHERE id = {entry_old[0]}"
        #query = f"REPLACE into {table_name} VALUES ({subquery1}) WHERE id = {entry_old[0]}"
        params = entry_new
        self.cur.execute(query, params)
        self.conn.commit()
        print(f"Entry {entry_new[0]} updated")
    
    def get_random_entries(self, table_name, amount):
        query = f"SELECT * from {table_name} ORDER BY RANDOM() LIMIT {amount}"
        self.cur.execute(query)
        entries = self.cur.fetchall()
        entries = [self.make_dict(self.cur, entry) for entry in entries]
        return entries

    def get_entry_by_id(self, table_name, id):
        query = f"SELECT * from {table_name} WHERE id = {id}"
        self.cur.execute(query)
        entry = self.cur.fetchone()
        if not entry:
            return None
        entry = self.make_dict(self.cur, entry)
        return entry

    # Returns a dictionary object, with table headings as keys and entry (tuple) values as value
    def make_dict(self, cursor, row):
        return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))


    def get_entries_by_heading(self, table_name, heading, value):
        query = f"SELECT * from {table_name} where {heading} = ?"
        params = value,
        self.cur.execute(query, params)
        entries = self.cur.fetchall()
        entries = [self.make_dict(self.cur, entry) for entry in entries]
        return entries

    def validate_user(self, username, password):
        query = f"SELECT * from users WHERE username = ? AND password = ?"
        params = (username, password)
        self.cur.execute(query, params)
        entries = self.cur.fetchall()
        entries = [self.make_dict(self.cur, entry) for entry in entries]
        if len(entries) == 1:
            return True
        return False
    
    # Get unique values for a chosen table heading, eg: product categories
    def get_unique_values(self, table_name, heading):
        query = f"SELECT DISTINCT {heading} from {table_name}"
        self.cur.execute(query)
        entries = self.cur.fetchall()
        entries = [entry[0] for entry in entries]
        return entries
# %%
