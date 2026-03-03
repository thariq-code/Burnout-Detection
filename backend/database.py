import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable not set")

client = MongoClient(MONGO_URI)
db = client.get_default_database()

users_collection = db["users"]
predictions_collection = db["predictions"]