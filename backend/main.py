from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, validator, EmailStr
from typing import Optional
from datetime import date, datetime
import re
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from urllib.parse import quote_plus
import bcrypt

username = os.getenv("MONGO_USERNAME", "")
password = os.getenv("MONGO_PASSWORD", "")
host = os.getenv("MONGO_HOST", "localhost")
port = os.getenv("MONGO_PORT", "27017")
db_name = os.getenv("MONGO_DB_NAME", "myapp")
user_collection = os.getenv("MONGO_USER_COLLECTION", "users")
shipments_collection = os.getenv("MONGO_SHIPMENTS_COLLECTION", "shipments")

# Escape special chars
safe_username = quote_plus(username) if username else ""
safe_password = quote_plus(password) if password else ""

# Build URI safely
if safe_username and safe_password:
    mongodb_uri = f"mongodb://{safe_username}:{safe_password}@{host}:{port}/?authSource=admin"
else:
    mongodb_uri = f"mongodb://{host}:{port}/"  # no auth

print(f"[INFO] Connecting to MongoDB: {host}:{port}, DB: {db_name}")


# 🔌 MongoDB Connection
client = MongoClient(mongodb_uri)
db = client[db_name]
users_col = db[user_collection]
shipments_col = db[shipments_collection]

app = FastAPI(title="Auth API")

# Password helpers (now used!)
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
@app.get("/")
def root():
    return {"message": "Auth & Shipment API is running!"}

#Keep your original /signup (form-style), but add hashing + DB insert
@app.post("/signup")
def signup(username: str, email: str, password: str, confirm_password: str):
    errors = []

    if len(username) <= 3:
        errors.append("Username must be more than 3 characters.")
    if "@" not in email or not email.endswith(".com"):
        errors.append("Invalid email: must contain '@' and end with '.com'.")
    if password != confirm_password:
        errors.append("Password does not match.")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter.")
    if not re.search(r"[0-9]", password):
        errors.append("Password must contain at least one digit.")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        errors.append("Password must contain at least one special character (e.g., !, @, #, $).")

    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="; ".join(errors)
        )

    # Check if user already exists
    if users_col.find_one({"email": email}):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered.")
    if users_col.find_one({"username": username}):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username already taken.")

    # Hash password & store in MongoDB
    hashed_pw = hash_password(password)
    result = users_col.insert_one({
        "username": username,
        "email": email,
        "password_hash": hashed_pw,   # never store plain password!
        "created_at": datetime.utcnow()
    })

    print(f"[SIGNUP] User '{username}' saved with ID: {result.inserted_id}")
    return {
        "message": f"Signup successful for {username}",
        "user_id": str(result.inserted_id)
    }

# Keep your original /login (form-style), but verify against DB + hash
@app.post("/login")
def login(email: str, password: str):
    if "@" not in email or not email.endswith(".com"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email: must contain '@' and end with '.com'."
        )

    # Fetch user from MongoDB
    user = users_col.find_one({"email": email})
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password.")

    # Verify hashed password
    if not verify_password(password, user["password_hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password.")

    print(f"[LOGIN] User '{email}' authenticated")
    return {
        "message": f"Login successful for {email}",
        "user_id": str(user["_id"])
    }

# Keep your Pydantic models (optional — not used in form routes, but safe to keep)
class SignupRequest(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str

    @validator("username")
    def validate_username(cls, v):
        if len(v) <= 3:
            raise ValueError("Username must be more than 3 characters.")
        return v

    @validator("email")
    def validate_email(cls, v):
        if "@" not in v or not v.endswith(".com"):
            raise ValueError("Invalid email: must contain '@' and end with '.com'.")
        return v

    @validator("password")
    def validate_password(cls, v, values):
        errors = []
        if len(v) < 8:
            errors.append("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", v):
            errors.append("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            errors.append("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", v):
            errors.append("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", v):
            errors.append("Password must contain at least one special character.")
        if 'confirm_password' in values and v != values['confirm_password']:
            errors.append("Password does not match.")
        if errors:
            raise ValueError("; ".join(errors))
        return v

class LoginRequest(BaseModel):
    email: str
    password: str

    @validator("email")
    def validate_email(cls, v):
        if "@" not in v or not v.endswith(".com"):
            raise ValueError("Invalid email: must contain '@' and end with '.com'.")
        return v

    @validator("password")
    def validate_password(cls, v):
        if len(v) == 0:
            raise ValueError("Password cannot be empty.")
        return v

# Shipment models & routes — unchanged (kept as-is)
from datetime import date
from typing import Optional

class Shipment(BaseModel):
    Shipment_Number: str
    Route_Details: str
    Device: str
    Po_Number: str
    NDC_Number: str
    Serial_Number_of_Goods: str
    Container_number: str
    Goods_Type: str
    Expected_Delivery_Date: date
    delivery_number: str
    Batch_ID: str
    Shipment_Description: str

from fastapi import Query

@app.get("/shipments", response_model=Shipment)
def read_shipments(
    Shipment_Number: str = Query(..., alias="Shiment_Number"),
    Route_Details: str = Query(...),
    Device: str = Query(...),
    Po_Number: str = Query(...),
    NDC_Number: str = Query(...),
    Serial_Number_of_Goods: str = Query(...),
    Container_number: str = Query(...),
    Goods_Type: str = Query(...),
    Expected_Delivery_Date: date = Query(...),
    delivery_number: str = Query(..., alias="delivary_number"),
    Batch_ID: str = Query(...),
    Shipment_Description: str = Query(...),
):
    return Shipment(
        Shipment_Number=Shipment_Number,
        Route_Details=Route_Details,
        Device=Device,
        Po_Number=Po_Number,
        NDC_Number=NDC_Number,
        Serial_Number_of_Goods=Serial_Number_of_Goods,
        Container_number=Container_number,
        Goods_Type=Goods_Type,
        Expected_Delivery_Date=Expected_Delivery_Date,
        delivery_number=delivery_number,
        Batch_ID=Batch_ID,
        Shipment_Description=Shipment_Description,
    )

@app.post("/shipments", response_model=Shipment)
def create_shipment(shipment: Shipment):
    # Store in MongoDB
    shipment_data = shipment.dict()
    shipment_data["created_at"] = datetime.utcnow()
    result = shipments_col.insert_one(shipment_data)
    shipment_data["id"] = str(result.inserted_id)
    
    print(f"[CREATE SHIPMENT] ID: {result.inserted_id}, Number: {shipment.Shipment_Number}")
    return shipment