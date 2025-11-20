<<<<<<< HEAD
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
=======
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import bcrypt
from pymongo.errors import ConnectionFailure

load_dotenv()

username = os.getenv("MONGO_USERNAME", "")
password = os.getenv("MONGO_PASSWORD", "")
host = os.getenv("MONGO_HOST", "localhost")
port = os.getenv("MONGO_PORT", "27017")
db_name = os.getenv("MONGO_DB_NAME", "fullstack")

safe_username = quote_plus(username) if username else ""
safe_password = quote_plus(password) if password else ""

if safe_username and safe_password:
    mongodb_uri = f"mongodb://{safe_username}:{safe_password}@{host}:{port}/?authSource=admin"
else:
    mongodb_uri = f"mongodb://{host}:{port}/"

print(f"[INFO] Connecting to MongoDB: {host}:{port}, DB: {db_name}")

try:
    client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("[INFO] Successfully connected to MongoDB.")
    db = client[db_name]
except ConnectionFailure as e:
    print(f"[ERROR] Could not connect to MongoDB: {e}")
    raise e
>>>>>>> c0dec9c98cd39b4d5a749bd0a276da4e2180991a


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
<<<<<<< HEAD
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
=======
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


class LoggedCollection:
    def __init__(self, collection, name):
        self._coll = collection
        self.name = name

    def insert_one(self, document):
        print(f"[DB INSERT] → {self.name}")
        return self._coll.insert_one(document)

    def find_one(self, *args, **kwargs):
        res = self._coll.find_one(*args, **kwargs)
        status = "✓ found" if res else "✗ not found"
        print(f"[DB FIND] → {self.name} | Query: {args[0] if args else kwargs} → {status}")
        return res

    def __getattr__(self, name):
        return getattr(self._coll, name)


users_col = LoggedCollection(db["users"], "users")
shipments_col = LoggedCollection(db["shipments"], "shipments")
>>>>>>> c0dec9c98cd39b4d5a749bd0a276da4e2180991a
