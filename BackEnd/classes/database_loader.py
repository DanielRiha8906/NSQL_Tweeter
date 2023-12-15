from pymongo import MongoClient

def connect_to_db(collection_name):
    client = MongoClient("mongodb://admin:admin@mongodb:27017", connect=False)
    dbname = client["nsql_sem"]
    collection = dbname[collection_name]
    return collection