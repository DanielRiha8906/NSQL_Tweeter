from pymongo import MongoClient


def DBD():
    client = MongoClient("mongodb://admin:admin@mongodb:27017", connect=False)
    dbname = client["nsql_sem"]
    collection = dbname["nsql_sem"]
    return collection
