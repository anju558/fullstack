from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date
from typing import Dict
import re

# Removed broken import for now (uncomment later when auth.py is ready)
# from auth import verify_password, hash_password, create_token, get_user

app = FastAPI(title="Auth API")
@app.get("/")
def read_root():
    return {"message": "Welcome to the Auth API"}

@app.post("/signup")  # 🔹 Use /signup for registration (not /signin)
def signup(username: str, email: str, password: str, confirm_password: str):
    errors = []

    # 1. Username: > 3 characters (you had this logic earlier)
    if len(username) <= 3:
        errors.append("Username must be more than 3 characters.")

    # 2. Email validation
    if "@" not in email or not email.endswith(".com"):
        errors.append("Invalid email: must contain '@' and end with '.com'.")

    # 3. Password match
    if password != confirm_password:
        errors.append("Password does not match.")  # ✅ Your requested message

    # 4. Password strength (8+ chars, upper, lower, digit, special)
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

    # Raise if any errors
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="; ".join(errors)  # 📝 Combined message (or use list for array response)
        )

    print(f"[SIGNUP] Username: {username}, Email: {email}, Password length: {len(password)}")
    return {"message": f"Signup successful for {username}", "email": email}



@app.post("/login")
def login(email: str, password: str):
    if "@" not in email or not email.endswith(".com"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email: must contain '@' and end with '.com'."
        )
    print(f"[LOGIN] Email: {email}, Password length: {len(password)}")
    return {"message": f"Login successful for {email}"}

from pydantic import BaseModel, validator

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", v):
            raise ValueError("Password must contain at least one special character.")
        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if values.get("password") != v:
            raise ValueError("Password does not match.")  # ✅ Exact message
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
@app.post("/signup")
def signup_endpoint(request: SignupRequest):
    print(f"[SIGNUP] Username: {request.username}, Email: {request.email}, Password length: {len(request.password)}")
    return {"message": f"Signup successful for {request.username}", "email": request.email} 


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
    Expected_Delivery_Date: date  # parsed automatically from ISO string (e.g., "2025-12-01")
    delivery_number: str
    Batch_ID: str
    Shipment_Description: str


from fastapi import Query

@app.get("/shipments", response_model=Shipment)
def read_shipments(
    Shipment_Number: str = Query(..., alias="Shiment_Number"),  # alias to accept old param name if needed
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
    print(f"[CREATE SHIPMENT] Shipment Number: {shipment.Shipment_Number}, Expected Delivery Date: {shipment.Expected_Delivery_Date}")
    return shipment