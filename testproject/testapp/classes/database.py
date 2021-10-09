# %%
# DB parameters
import sqlite3

class Database(object):
    def __init__(self):


        self.path_db = "db_sqlite/ecommerce.db"
        self.path_products = "data/awae_products.xlsx"
        self.path_accounts = "data/awae_accounts.xlsx"


        self.conn = None
        self.cur = None
        self.tables = None

    def connect(self):
        conn = sqlite3.connect(self.path_db)
        cur = conn.cursor()
        self.conn = conn
        self.cur = cur
        print("db connected")
        return conn, cur
    
    def close(self):
        self.db.close()
        self.db = None
        self.cur = None
        print("db closed")



# # To prevent SQL injection and for better database security, we must use wildcards instead of variable names in the query
# wildcards = {
#     "products": "?, ?, ?, ?, ?, ?, ?, ?",
#     "accounts": "?, ?, ?, ?, ?, ?, ?"
# }