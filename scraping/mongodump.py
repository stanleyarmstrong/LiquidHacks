import os
import json
from pymongo import MongoClient
from pathlib import Path

if __name__ == "__main__":
    username = os.getenv('MONGO_USER')
    password = os.getenv('MONGO_PASS')
    #print(username)
    #print(password)
    dbname = "MouseData"
    collectionname = "test"

    client = MongoClient(f"mongodb+srv://{username}:{password}@liquidmouse.8pyh5.mongodb.net")
    db = client[dbname]
    test_collection = db[collectionname]
    print(db)

    for document in test_collection.find():
        print(document)

    with open(Path('./mice.json')) as f:
        data = json.load(f)

    for mouse in data:
        print(mouse['name'])
        test_collection.find_one_and_replace({'name': mouse['name']}, mouse, upsert=True)