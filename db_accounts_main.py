# %%
import sqlite3
import pandas as pd
from db_helpers import *
from django.contrib.auth.models import User

table_name = "accounts"

# Create account DB and fill with accounts
db, cur = db_connect(path_db)
table_drop(cur, table_name)
table_create(cur, table_name, table_identifiers[table_name])
table_fill(db, cur, table_name, wildcards[table_name], path_accounts)
# %%
