from fastapi import FastAPI, HTTPException, status, Query, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, date
from jose import JWTError, jwt
from models import Shipment
import re

# Import database helpers
from database import users_col, shipments_col, hash_password, verify_password

app = FastAPI(title="SCMXPERTLITE", version="1.0.0")

# === JWT CONFIG ===
SECRET_KEY = "mysecretkey123"  # Move this to .env in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Tell Swagger we use Bearer tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# === JWT HELPER FUNCTIONS ===
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create JWT token with expiration"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str = Depends(oauth2_scheme)):
    """Automatically extracts JWT from Authorization: Bearer <token>"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        password_hash = payload.get("password_hash")
        if email is None or password_hash is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token payload.")
        return {"email": email, "password_hash": password_hash}
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token.")


# === ROOT ROUTE ===
@app.get("/")
def root():
    return {"message": "Auth & Shipment API with JWT (Email + Password) is running!"}


# === AUTH ROUTES ===
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
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "; ".join(errors))

    if users_col.find_one({"email": email}):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered.")
    if users_col.find_one({"username": username}):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username already taken.")

    hashed_pw = hash_password(password)
    result = users_col.insert_one({
        "username": username,
        "email": email,
        "password_hash": hashed_pw,
        "created_at": datetime.utcnow()
    })

    print(f"[SIGNUP] User '{username}' saved with ID: {result.inserted_id}")
    return {"message": f"Signup successful for {username}"}


# ⚙️ LOGIN now supports Swagger auth flow
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    email = form_data.username  # Swagger uses "username" field for email
    password = form_data.password

    user = users_col.find_one({"email": email})
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password.")

    # ✅ JWT now includes both email and hashed password
    access_token = create_access_token(data={
        "email": email,
        "password_hash": user["password_hash"]  # store hashed password safely
    })

    print(f"[LOGIN] {email} → JWT issued with email and hashed password")
    return {"access_token": access_token, "token_type": "bearer"}


# === PROTECTED ROUTE ===
@app.get("/profile")
def profile(user: dict = Depends(verify_token)):
    """Use email and password from JWT"""
    db_user = users_col.find_one({"email": user["email"]})
    if not db_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    return {
        "email": db_user["email"],
        "username": db_user["username"],
        "stored_password_hash": db_user["password_hash"],
        "token_password_hash": user["password_hash"]
    }


# === SHIPMENT ROUTES ===
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
def create_shipment(shipment: Shipment, user: dict = Depends(verify_token)):
    """Record who created the shipment using email from JWT"""
    shipment_data = shipment.dict()
    shipment_data["created_by_email"] = user["email"]
    shipment_data["created_at"] = datetime.utcnow()
    result = shipments_col.insert_one(shipment_data)
    shipment_data["id"] = str(result.inserted_id)

    print(f"[CREATE SHIPMENT] Created by '{user['email']}' | ID: {result.inserted_id}")
    return shipment
