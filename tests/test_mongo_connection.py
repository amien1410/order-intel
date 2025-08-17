from db.mongo.mongo_connection import get_database

def test_connection():
    db = get_database()
    assert db.name == "ai_training"
