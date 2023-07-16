from pymongo import MongoClient

def get_database():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["test_database"]
    # print("Connected to the MongoDB database!")

    return db