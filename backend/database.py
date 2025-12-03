import os
from dotenv import load_dotenv
from pymongo import MongoClient
import bcrypt

# Load .env file
load_dotenv()

# ------------------------------
# Read MongoDB Connection Values
# ------------------------------
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")  # FIXED

USERS_COLLECTION_NAME = os.getenv("USERS_COLLECTION")
SHIPMENTS_COLLECTION_NAME = os.getenv("SHIPMENTS_COLLECTION")
DEVICE_COLLECTION_NAME = os.getenv("DEVICE_DATA_COLLECTION")

# Debugging prints
print("Loaded DB_NAME:", DB_NAME)
print("Loaded USERS_COLLECTION:", USERS_COLLECTION_NAME)
print("Loaded SHIPMENTS_COLLECTION:", SHIPMENTS_COLLECTION_NAME)
print("Loaded DEVICE_DATA_COLLECTION:", DEVICE_COLLECTION_NAME)

# ------------------------------
# Connect to MongoDB
# ------------------------------
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
users_col = db[USERS_COLLECTION_NAME]
shipments_col = db[SHIPMENTS_COLLECTION_NAME]
device_col = db[DEVICE_COLLECTION_NAME]
stream_col = db[os.getenv("STREAM_COLLECTION", "device_streams")]

# Password Hashing
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )
