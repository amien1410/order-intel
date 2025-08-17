def create_collections(db):
    db.create_collection("customers")
    db.create_collection("products")
    db.create_collection("transactions")
    print("Collections created successfully!")
