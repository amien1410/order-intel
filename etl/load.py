from db.mongo.mongo_connection import get_database

def load_to_mongo(records, collection_name="transactions"):
    db = get_database()
    collection = db[collection_name]
    if records:
        collection.insert_many(records)
        print(f"Inserted {len(records)} records into {collection_name}.")
