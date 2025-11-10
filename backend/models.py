# models.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime 

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None

class UserInDB(UserCreate):
    id: str  # MongoDB ObjectId as string
    created_at: datetime
    password_hash: str  # Store hashed password only
class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    age: Optional[int] = None
    created_at: datetime
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
class TokenData(BaseModel):
    email: Optional[str] = None
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
    id: str  # MongoDB ObjectId as string
class ShipmentOut(Shipment):
    id: str
    created_at: datetime
    