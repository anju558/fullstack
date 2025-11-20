from fastapi import FastAPI, Request, Form, HTTPException, status, Depends
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
import re

from jose import JWTError
import jwt

# DB helpers
from main import BASE_DIR
from database import hash_password, verify_password
from auth import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
import os
import bcrypt
from dotenv import load_dotenv

load_dotenv()

mongodb_uri = os.getenv("MONGO_URI")
users_col = os.getenv("USERS_COLLECTION")
shipments_col = os.getenv("SHIPMENTS_COLLECTION")  


app = FastAPI(
    title="SCMXPERTLITE",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Mount static + templates
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Decode JWT
async def get_current_user_email(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception


@app.get("/api/devices")
async def get_devices_api():
    # JSON API used by client-side polling/JS
    devices = list(shipments_col.find({}, {"_id": 0}))
    return {"devices": devices}


@app.get("/devices", response_class=HTMLResponse)
def devices_page(request: Request):
    # Render server page that lists devices and links to stream pages
    devices = list(shipments_col.find({}, {"_id": 0}))
    return templates.TemplateResponse("devices.html", {"request": request, "devices": devices})


def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ✅ Both /login and /login.html supported
@app.get("/login", response_class=HTMLResponse)
@app.get("/login.html", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    lookup_email = username.strip().lower()
    user = users_col.find_one({"email": lookup_email})
    if not user or not verify_password(password, user["password_hash"]):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password."}, status_code=401)

    token = create_access_token({"email": user["email"], "username": user.get("username")})
    resp = RedirectResponse(url="/dashboard", status_code=302)
    resp.set_cookie(key="access_token", value=token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return resp


# ✅ Both /signup and /signup.html supported
@app.get("/signup", response_class=HTMLResponse)
@app.get("/signup.html", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup")
async def signup(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    errors = []
    email = email.strip().lower()

    if len(username) <= 3:
        errors.append("Username must be more than 3 characters.")
    if "@" not in email or "." not in email.split('@')[-1]:
        errors.append("Invalid email address.")
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
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
        errors.append("Password must contain at least one special character.")

    if users_col.find_one({"email": email}):
        errors.append("Email already registered.")
    if users_col.find_one({"username": username}):
        errors.append("Username already taken.")

    if errors:
        return templates.TemplateResponse("signup.html", {"request": request, "errors": errors}, status_code=400)

    hashed_pw = hash_password(password)
    users_col.insert_one({
        "username": username,
        "email": email,
        "password_hash": hashed_pw,
        "created_at": datetime.utcnow()
    })

    token = create_access_token({"email": email, "username": username})
    resp = RedirectResponse(url="/dashboard", status_code=302)
    resp.set_cookie(key="access_token", value=token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return resp


@app.get("/logout")
def logout():
    resp = RedirectResponse(url="/login")
    resp.delete_cookie("access_token")
    return resp


def get_current_user_from_request(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    payload = decode_token(token)
    if not payload:
        return None
    email = payload.get("email")
    return users_col.find_one({"email": email})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = get_current_user_from_request(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("dashboard.html", {"request": request, "username": user.get("username")})


@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request):
    user = get_current_user_from_request(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("profile.html", {"request": request, "username": user.get("username")})


@app.get("/api/profile")
async def get_profile(request: Request):
    user = get_current_user_from_request(request)
    if not user:
        return JSONResponse({"detail": "Not authenticated"}, status_code=401)
    
    return {
        "username": user.get("username"),
        "email": user.get("email"),
        "created_at": user.get("created_at").isoformat() if user.get("created_at") else None,
        "id": str(user.get("_id"))
    }


@app.get("/create-shipment", response_class=HTMLResponse)
def create_shipment_page(request: Request):
    # Only authenticated users can create shipments
    user = get_current_user_from_request(request)
    if not user:
        return RedirectResponse(url="/login")

    # Generate a short-lived captcha token (simple math) using access token helper
    import random
    from datetime import timedelta as _td

    a = random.randint(1, 9)
    b = random.randint(1, 9)
    captcha_question = f"{a} + {b} = ?"
    captcha_token = create_access_token({"captcha": a + b}, expires_delta=_td(minutes=5))

    return templates.TemplateResponse("create_shipment.html", {"request": request, "captcha_question": captcha_question, "captcha_token": captcha_token})


@app.post("/create-shipment")
async def create_shipment_handler(request: Request):
    user = get_current_user_from_request(request)
    if not user:
        return RedirectResponse(url="/login")

    form = await request.form()
    # verify captcha
    captcha_answer = form.get("captcha_answer")
    captcha_token = form.get("captcha_token")
    payload = decode_token(captcha_token) if captcha_token else None
    if not payload or str(payload.get("captcha")) != str(captcha_answer):
        # Return to form with an error
        return templates.TemplateResponse("create_shipment.html", {"request": request, "error": "Invalid or expired captcha. Please try again."}, status_code=400)

    # Build shipment object from form (preserve same field names used in dashboard modal)
    shipment = dict(form)
    # remove captcha fields
    shipment.pop("captcha_answer", None)
    shipment.pop("captcha_token", None)

    shipment["created_by_email"] = user["email"]
    shipment["created_at"] = datetime.utcnow()
    shipments_col.insert_one(shipment)

    # Redirect to my-shipments instead of dashboard
    return RedirectResponse(url="/my-shipments", status_code=302)


@app.get("/my-shipments", response_class=HTMLResponse)
def my_shipments_page(request: Request):
    user = get_current_user_from_request(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("my_shipments.html", {"request": request, "username": user.get("username")})


@app.get("/api/my-shipments")
async def get_my_shipments(request: Request):
    user = get_current_user_from_request(request)
    if not user:
        return JSONResponse({"detail": "Not authenticated"}, status_code=401)
    
    shipments = list(shipments_col.find({"created_by_email": user["email"]}, {"_id": 0}))
    return {"shipments": shipments}


@app.get("/view-stream", response_class=HTMLResponse)
def view_stream_page(request: Request):
    user = get_current_user_from_request(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("view_stream.html", {"request": request})


@app.get("/device-stream/{device_id}", response_class=HTMLResponse)
def device_stream_page(request: Request, device_id: str):
    # Render a page that polls the API for device updates and shows details
    # Try to find a representative device record (if any)
    device_doc = shipments_col.find_one({"Device": device_id}, {"_id": 0})
    return templates.TemplateResponse("device_stream.html", {"request": request, "device": device_doc, "device_id": device_id})
