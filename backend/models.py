from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
import re


# -------------------------
# User Models
# -------------------------

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None


class UserInDB(UserCreate):
    id: str                     # MongoDB document ID as string
    created_at: datetime
    password_hash: str          # Store hashed password only


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    age: Optional[int] = None
    created_at: datetime


# -------------------------
# Authentication Models
# -------------------------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


# -------------------------
# Shipment Models
# -------------------------

class Shipment(BaseModel):
    Shipment_Number: str
    Route_Details: str
    Device: str
    Po_Number: str
    NDC_Number: str
    Serial_Number_of_Goods: str
    Container_number: str
    Goods_Type: str
    Expected_Delivery_Date: datetime
    delivery_number: str
    Batch_ID: str
    Shipment_Description: str
    created_at: datetime


class ShipmentInDB(Shipment):
    id: str


class ShipmentOut(Shipment):
    id: str
    created_at: datetime


# -------------------------
# Signup / Login Validation
# -------------------------

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
        if ("confirm_password" in values) and (v != values["confirm_password"]):
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
