import os
from dotenv import load_dotenv
from pymongo import MongoClient
from random import choice

load_dotenv()



# print(os.getenv("CONNECTION_STRING"))

def DB(collectionName="Terminy"):
    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = os.getenv("CONNECTION_STRING")

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)
    dbname = client["LaborkyDB"]
    collection = dbname[collectionName]
    return collection

# DB("Collection").insert_one({"_id":123331,"tester":"pokus"})