from fastapi import FastAPI, Request, Form, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from jose import JWTError, jwt
from datetime import datetime, timedelta
from models import Shipment
import re

# DB helpers
from database import users_col, shipments_col, hash_password, verify_password
from auth import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="SCMXPERTLITE", version="1.0.0")

# Mount static files and configure templates
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    # username is email in the forms
    user = users_col.find_one({"email": username})
    if not user or not verify_password(password, user["password_hash"]):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password."}, status_code=401)

    token = create_access_token({"email": user["email"], "username": user.get("username")})
    resp = RedirectResponse(url="/dashboard", status_code=302)
    resp.set_cookie(key="access_token", value=token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return resp


@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup")
async def signup(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
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
    if not re.search(r"[!@#$%^&*()_+\-=[\]{};':\"\\|,.<>\/?)", password):
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


@app.post("/shipments")
async def create_shipment(request: Request):
    user = get_current_user_from_request(request)
    if not user:
        return JSONResponse({"detail": "Not authenticated"}, status_code=401)

    # Accept form or JSON
    if request.headers.get("content-type", "").startswith("application/json"):
        payload = await request.json()
    else:
        form = await request.form()
        payload = dict(form)

    payload["created_by_email"] = user["email"]
    payload["created_at"] = datetime.utcnow()
    result = shipments_col.insert_one(payload)
    return {"id": str(result.inserted_id)}
