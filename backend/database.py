
from pymongo import MongoClient
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")


try:
    client = MongoClient(mongo_uri)
    

    client.admin.command('ping') 
    print("Successfully connected to MongoDB!")

except Exception as e:
    print(f"ERROR: Could not connect to MongoDB: {e}")

db = client["project_db"]

users = db["users"]
