# database.py
from pymongo import MongoClient
from pymongo.collection import Collection
import bcrypt
from dotenv import load_dotenv
import os
# from config import DATA_BASE, MONGO_URI, SHIPMENTS_COLLECTION, USERS_COLLECTION
# from config import MONGO_URI, DATA_BASE, USERS_COLLECTION, SHIPMENTS_COLLECTION
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATA_BASE = os.getenv("DATA_BASE", "scm")
USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")
SHIPMENTS_COLLECTION = os.getenv("SHIPMENTS_COLLECTION", "shipments")


# MongoDB client & DB
client = MongoClient(MONGO_URI)
db = client[DATA_BASE]

# Collections
users_col: Collection = db[USERS_COLLECTION]
shipments_col: Collection = db[SHIPMENTS_COLLECTION]


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))