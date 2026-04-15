from pymongo import MongoClient
from flask import current_app

_db = None

def get_db():
    """
    Returns a MongoDB database instance.
    Uses app config to connect to the correct database.
    """
    global _db
    if _db is None:
        client = MongoClient(current_app.config['MONGODB_URI'])
        _db = client[current_app.config['DB_NAME']]
    return _db
