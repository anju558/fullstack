# database.py
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import bcrypt

load_dotenv()  # Load environment variables

# --- MongoDB Config ---
username = os.getenv("MONGO_USERNAME", "")
password = os.getenv("MONGO_PASSWORD", "")
host = os.getenv("MONGO_HOST", "localhost")
port = os.getenv("MONGO_PORT", "27017")
db_name = os.getenv("MONGO_DB_NAME", "myapp")
user_collection_name = os.getenv("MONGO_USER_COLLECTION", "users")
shipments_collection_name = os.getenv("MONGO_SHIPMENTS_COLLECTION", "shipments")

# Escape special characters for URI
safe_username = quote_plus(username) if username else ""
safe_password = quote_plus(password) if password else ""

# Build URI
if safe_username and safe_password:
    mongodb_uri = f"mongodb://{safe_username}:{safe_password}@{host}:{port}/?authSource=admin"
else:
    mongodb_uri = f"mongodb://{host}:{port}/"

print(f"[INFO] Connecting to MongoDB: {host}:{port}, DB: {db_name}")

# --- MongoDB Client & Collections ---
client = MongoClient(mongodb_uri)
db = client[db_name]
users_col = db[user_collection_name]
shipments_col = db[shipments_collection_name]

# --- Password Utilities ---
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
# In database.py, after defining collections:

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
        # fallback to original collection for other methods (e.g., update_one, delete_one)
        return getattr(self._coll, name)

# Wrap your collections:
users_col = LoggedCollection(db[user_collection_name], "users")
shipments_col = LoggedCollection(db[shipments_collection_name], "shipments")
