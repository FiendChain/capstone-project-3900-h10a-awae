# %%
# Embed or not?
# do you need the embedded data 80% of the time
# How often you want the embedded data without document?
# is embedded data bounded?
# ratings should be ok as an unboudned set to embed

from pymongo import MongoClient
from pprint import pprint

# Create a client that can host databases
client = MongoClient("mongodb://localhost:12343/")
# client = MongoClient("localhost", "27017") # same thing
# create database
db = client["myfirstdatabase"]
print(client.list_database_names())
print(db.list_collection_names())

# Create collection
# Note: collection is not created until one document is inserted
col1 = db["customers"]

# Insert one document
# x = col1.insert_one({
#     "name": "John",
#     "address" : "ok street"
# })
# print(x.inserted_id)


x = col1.insert_one({
    "name": "Sarah",
    "address" : "kek street"
})
# print(x.inserted_id)

# Insert multiple documents
# _id field can be manually specified, or let mongoDB generate one
# mylist = [
#   { "_id": 31, "name": "John", "address": "Highway 37"},
#   { "_id": 32, "name": "Peter", "address": "Lowstreet 27"},
#   { "_id": 33, "name": "Amy", "address": "Apple st 652"},
#   { "_id": 34, "name": "Hannah", "address": "Mountain 21"},
#   { "_id": 35, "name": "Michael", "address": "Valley 345"},
#   { "_id": 36, "name": "Sandy", "address": "Ocean blvd 2"},
#   { "_id": 37, "name": "Betty", "address": "Green Grass 1"},
#   { "_id": 38, "name": "Richard", "address": "Sky st 331"},
#   { "_id": 39, "name": "Susan", "address": "One way 98"},
#   { "_id": 310, "name": "Vicky", "address": "Yellow Garden 2"},
#   { "_id": 311, "name": "Ben", "address": "Park Lane 38"},
#   { "_id": 312, "name": "William", "address": "Central st 954"},
#   { "_id": 313, "name": "Chuck", "address": "Main Road 989"},
#   { "_id": 314, "name": "Viola", "address": "Sideway 1633"}
# ]
# x = col1.insert_many(mylist)
#print(x.inserted_ids)

# Find one document
# x = col1.find_one()
# print(x)

# find all
# pram 1: query object. leave empty to select all documents in collection
# param 2: which fields to include/exclude. 0 = exclude, 1 = include. All fields must be either 1 or 0 (with exception of _id)
# no parameters is equivalent to select * in SQL
for x in col1.find():
    print(x)

# for x in col1.find({}, {"address": 0}):
#     print(x)

# for x in col1.find({}, {"name": 1, "_id": 0}):
#     print(x)

# x = col1.delete_many({})
# print(x.deleted_count, " documents deleted.")

x = col1.insert_one({
    "name": "John",
    "address" : "ok street"
})
for x in col1.find():
    print(x)
#print(col1.drop())
