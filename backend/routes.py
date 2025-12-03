# backend/routes.py
from fastapi import APIRouter, Request, Form, HTTPException, status, Depends, Response
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi_mail import MessageSchema, FastMail
from pathlib import Path
from datetime import datetime, timedelta, timezone
import re
from jose import jwt
import secrets
import httpx
from typing import Optional, Dict, List
from time import time

# --- Config & DB ---
from backend.config import mail_conf, RECAPTCHA_SITE_KEY, RECAPTCHA_SECRET_KEY
from backend.database import users_col, shipments_col, device_col, stream_col, hash_password, verify_password
from backend.auth import create_access_token, get_current_user_email, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# --- Global instances ---
fm = FastMail(mail_conf)

# ✅ OTP store — in-memory (replace with Redis in prod)
otp_store: Dict[str, Dict] = {}

# ✅ Rate limiter: email → list of timestamps (last 10 min only)
otp_request_log: Dict[str, List[float]] = {}

BASE_DIR = Path(__file__).resolve().parent.parent
app = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# ---------------------
# Cookie / JWT helpers
# ---------------------
def get_user_from_cookies(request: Request) -> Optional[Dict]:
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if not email:
            return None
        return users_col.find_one({"email": email})
    except Exception:
        return None


def render_template(template: str, ctx: dict, status_code: int = 200) -> HTMLResponse:
    return templates.TemplateResponse(template, ctx, status_code=status_code)


# ---------------------
# Public / utility routes
# ---------------------
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return render_template("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
@app.get("/login.html", response_class=HTMLResponse)
def login_page(request: Request):
    signup_success = request.query_params.get("signup") == "success"
    error = request.query_params.get("error")
    return render_template("login.html", {"request": request, "signup_success": signup_success, "error": error})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    email = username.strip().lower()
    user = users_col.find_one({"email": email})
    if not user or not verify_password(password, user.get("password_hash", "")):
        return render_template("login.html", {"request": request, "error": "Invalid email or password."}, status_code=401)

    token = create_access_token({"email": user["email"], "username": user.get("username", "")})
    resp = RedirectResponse("/dashboard", status_code=303)
    resp.set_cookie("access_token", token, httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    resp.set_cookie("username", user.get("username", ""), max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    resp.set_cookie("email", user["email"], max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return resp


@app.get("/signup", response_class=HTMLResponse)
@app.get("/signup.html", response_class=HTMLResponse)
def signup_page(request: Request):
    return render_template("signup.html", {"request": request, "recaptcha_site_key": RECAPTCHA_SITE_KEY})


@app.post("/signup")
async def signup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    g_recaptcha_response: Optional[str] = Form(None, alias="g-recaptcha-response")
):
    username = username.strip()
    email = email.strip().lower()
    errors = []

    if len(username) <= 3:
        errors.append("Username must be more than 3 characters.")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors.append("Invalid email address.")
    if password != confirm_password:
        errors.append("Password does not match.")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain uppercase.")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain lowercase.")
    if not re.search(r"[0-9]", password):
        errors.append("Password must contain digit.")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", password):
        errors.append("Password must contain special character.")

    if users_col.find_one({"email": email}):
        errors.append("Email already registered.")
    if users_col.find_one({"username": username}):
        errors.append("Username already taken.")

    # reCAPTCHA
    if RECAPTCHA_SECRET_KEY:
        if not g_recaptcha_response:
            errors.append("reCAPTCHA failed")
        else:
            async with httpx.AsyncClient() as client:
                # ✅ FIXED: removed trailing spaces in URL
                resp = await client.post(
                    "https://www.google.com/recaptcha/api/siteverify",
                    data={"secret": RECAPTCHA_SECRET_KEY, "response": g_recaptcha_response}
                )
                if not resp.json().get("success"):
                    errors.append("reCAPTCHA failed")

    if errors:
        return render_template(
            "signup.html",
            {"request": request, "errors": errors, "recaptcha_site_key": RECAPTCHA_SITE_KEY},
            status_code=400
        )

    hashed_pw = hash_password(password)
    users_col.insert_one({
        "username": username,
        "email": email,
        "password_hash": hashed_pw,
        "created_at": datetime.now(timezone.utc)
    })
    return RedirectResponse("/login?signup=success", status_code=303)


@app.get("/logout")
def logout(response: Response):
    resp = RedirectResponse("/login")
    resp.delete_cookie("access_token")
    resp.delete_cookie("username")
    resp.delete_cookie("email")
    return resp


# ---------------------
# OTP-based Password Reset
# ---------------------
@app.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(request: Request):
    return render_template("forgot-password.html", {"request": request})


@app.post("/forgot-password")
async def forgot_password(request: Request, email: str = Form(...)):
    email = email.strip().lower()

    # ✅ Rate limiting: max 3 requests per 10 minutes per email
    now = time()
    otp_request_log[email] = [t for t in otp_request_log.get(email, []) if now - t < 600]  # keep last 10 min
    if len(otp_request_log[email]) >= 3:
        return render_template("forgot-password.html", {
            "request": request,
            "error": "Too many requests. Please try again in 10 minutes."
        })

    user = users_col.find_one({"email": email})
    # ✅ Avoid email enumeration: still respond positively
    if not user:
        return render_template("forgot-password.html", {
            "request": request,
            "message": "If the email is registered, an OTP has been sent."
        })

    # Generate 6-digit OTP
    otp = f"{secrets.randbelow(1000000):06}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    # Store
    otp_store[email] = {"otp": otp, "expires_at": expires_at}
    otp_request_log[email].append(now)

    # Send email
    try:
        message = MessageSchema(
            subject="ShipTrack — Password Reset OTP",
            recipients=[email],
            body=f"Your ShipTrack password reset code is:\n\n{otp}\n\nValid for 10 minutes.",
            subtype="plain"
        )
        await fm.send_message(message)  # ✅ reuse global `fm`
    except Exception as e:
        print("📧 Email send failed:", e)
        return render_template("forgot-password.html", {
            "request": request,
            "error": "Failed to send OTP. Please try again."
        })

    # Redirect + bind email securely
    response = RedirectResponse(url="/verify-otp", status_code=303)
    response.set_cookie(
        key="reset_email",
        value=email,
        httponly=True,
        secure=request.url.scheme == "https",
        max_age=600,
        samesite="lax"
    )
    return response


@app.get("/verify-otp", response_class=HTMLResponse)
def verify_otp_page(request: Request):
    reset_email = request.cookies.get("reset_email")
    if not reset_email:
        return RedirectResponse("/forgot-password", status_code=303)
    return render_template("verify-otp.html", {"request": request})


@app.post("/verify-otp")
async def verify_otp(
    request: Request,
    otp: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    reset_email = request.cookies.get("reset_email")
    if not reset_email:
        return RedirectResponse("/forgot-password", status_code=303)

    record = otp_store.get(reset_email)
    if not record:
        return render_template("verify-otp.html", {
            "request": request,
            "error": "Session expired. Please request a new OTP."
        })

    now = datetime.now(timezone.utc)
    if now > record["expires_at"]:
        otp_store.pop(reset_email, None)
        return render_template("verify-otp.html", {
            "request": request,
            "error": "OTP expired. Please request a new one."
        })

    if otp != record["otp"]:
        return render_template("verify-otp.html", {
            "request": request,
            "error": "Invalid OTP. Please check and try again."
        })

    if new_password != confirm_password:
        return render_template("verify-otp.html", {
            "request": request,
            "error": "Passwords do not match."
        })

    # ✅ Password strength validation (reuse signup logic)
    errors = []
    if len(new_password) < 8:
        errors.append("Password must be at least 8 characters.")
    if not re.search(r"[A-Z]", new_password):
        errors.append("Must contain uppercase letter.")
    if not re.search(r"[a-z]", new_password):
        errors.append("Must contain lowercase letter.")
    if not re.search(r"[0-9]", new_password):
        errors.append("Must contain a digit.")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", new_password):
        errors.append("Must contain a special character (e.g., !, @, #).")

    if errors:
        return render_template("verify-otp.html", {
            "request": request,
            "error": " ".join(errors)
        })

    # Update password
    try:
        hashed_pw = hash_password(new_password)
        result = users_col.update_one({"email": reset_email}, {"$set": {"password_hash": hashed_pw}})
        if result.matched_count == 0:
            raise Exception("User not found during update")
        otp_store.pop(reset_email, None)
    except Exception as e:
        print("❌ DB update failed:", e)
        return render_template("verify-otp.html", {
            "request": request,
            "error": "Failed to update password. Please try again."
        })

    # Cleanup & redirect
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("reset_email")
    return response


# ---------------------
# Protected HTML routes
# ---------------------
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    user = get_user_from_cookies(request)
    if not user:
        return RedirectResponse("/login")
    return render_template("dashboard.html", {"request": request, "username": user.get("username")})


@app.get("/profile", response_class=HTMLResponse)
def profile_page(request: Request):
    user = get_user_from_cookies(request)
    if not user:
        return RedirectResponse("/login")
    return render_template("profile.html", {
        "request": request,
        "username": user.get("username"),
        "email": user.get("email"),
        "created_at": user.get("created_at")
    })


@app.get("/profile-data")
def profile_data(request: Request):
    user = get_user_from_cookies(request)
    if not user:
        return JSONResponse({"error": "Not authenticated"}, status_code=401)
    return {
        "username": user["username"],
        "email": user["email"],
        "created_at": user.get("created_at")
    }


@app.get("/devices", response_class=HTMLResponse)
def devices_page(request: Request):
    user = get_user_from_cookies(request)
    if not user:
        return RedirectResponse("/login")
    pipeline = [
        {"$sort": {"timestamp": -1}},
        {"$group": {"_id": "$Device_ID", "latest": {"$first": "$$ROOT"}}},
        {"$replaceRoot": {"newRoot": "$latest"}}
    ]
    device_readings = list(device_col.aggregate(pipeline))
    device_ids = [d["Device_ID"] for d in device_readings if d.get("Device_ID")]
    shipments = list(shipments_col.find({"Device": {"$in": device_ids}}, {
        "Device": 1, "Route_From": 1, "Route_To": 1, "_id": 0
    }))
    route_map = {s["Device"]: {"Route_From": s.get("Route_From", "—"), "Route_To": s.get("Route_To", "—")} for s in shipments}
    for d in device_readings:
        dev_id = d.get("Device_ID")
        if dev_id in route_map:
            d.update(route_map[dev_id])
        else:
            d.setdefault("Route_From", "—")
            d.setdefault("Route_To", "—")
    return render_template("devices.html", {"request": request, "devices": device_readings})


@app.get("/my-shipments", response_class=HTMLResponse)
def my_shipments_page(request: Request):
    user = get_user_from_cookies(request)
    if not user:
        return RedirectResponse("/login")
    email = user.get("email")
    query_param = request.query_params.get("shipment", "").strip()
    db_query = {"created_by_email": email}
    if query_param:
        db_query["$or"] = [
            {"Shipment": {"$regex": query_param, "$options": "i"}},
            {"Shipment_Number": {"$regex": query_param, "$options": "i"}},
            {"Device": {"$regex": query_param, "$options": "i"}},
            {"_id": {"$regex": query_param, "$options": "i"}}
        ]
    shipments = list(shipments_col.find(db_query, {"_id": 0}))
    return render_template("my_shipments.html", {
        "request": request,
        "username": user.get("username"),
        "email": email,
        "shipments": shipments,
        "search_query": query_param
    })


@app.get("/view-stream", response_class=HTMLResponse)
def view_stream_page(request: Request):
    user = get_user_from_cookies(request)
    if not user:
        return RedirectResponse("/login")
    devices = list(shipments_col.find({}, {"_id": 0, "Device": 1}))
    device_list = sorted({d.get("Device") for d in devices if d.get("Device")})
    selected_device = request.query_params.get("device", "").strip()
    stream_data = []
    if selected_device:
        stream_data = list(device_col.find({"Device_ID": selected_device}).sort("timestamp", -1).limit(50))
        for doc in stream_data:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            if isinstance(doc.get("timestamp"), datetime):
                doc["timestamp"] = doc["timestamp"].isoformat()
    return render_template("view_stream.html", {
        "request": request,
        "devices": device_list,
        "selected_device": selected_device,
        "stream_data": stream_data
    })


@app.get("/api/stream/{device}")
async def get_device_stream_api(device: str, email: str = Depends(get_current_user_email)):
    stream_docs = list(stream_col.find({"device": device}).sort("timestamp", -1).limit(50))
    for doc in stream_docs:
        doc["_id"] = str(doc["_id"])
        if isinstance(doc.get("timestamp"), datetime):
            doc["timestamp"] = doc["timestamp"].isoformat()
    return {"device": device, "stream_data": stream_docs}


@app.get("/device-stream/{device_id}", response_class=HTMLResponse)
def device_stream_page(request: Request, device_id: str):
    user = get_user_from_cookies(request)
    if not user:
        return RedirectResponse("/login")
    device_doc = shipments_col.find_one({"Device": device_id}, {"_id": 0}) or {}
    return render_template("device_stream.html", {
        "request": request,
        "device": device_doc,
        "device_id": device_id
    })


@app.get("/create-shipment", response_class=HTMLResponse)
def create_shipment_page(request: Request):
    user = get_user_from_cookies(request)
    if not user:
        return RedirectResponse("/login")
    import random
    a, b = random.randint(1, 9), random.randint(1, 9)
    captcha_question = f"{a} + {b} = ?"
    captcha_token = create_access_token({"captcha": a + b}, expires_delta=timedelta(minutes=5))
    return render_template("create_shipment.html", {
        "request": request,
        "captcha_question": captcha_question,
        "captcha_token": captcha_token
    })


@app.post("/create-shipment")
async def create_shipment_handler(request: Request):
    user = get_user_from_cookies(request)
    if not user:
        return RedirectResponse("/login")
    form = await request.form()
    captcha_answer = form.get("captcha_answer")
    captcha_token = form.get("captcha_token")
    try:
        payload = jwt.decode(captcha_token, SECRET_KEY, algorithms=[ALGORITHM])
        if str(payload.get("captcha")) != str(captcha_answer):
            raise ValueError("captcha mismatch")
    except Exception:
        return render_template("create_shipment.html", {
            "request": request,
            "error": "Invalid or expired captcha."
        }, status_code=400)
    shipment = {k: v for k, v in form.items() if k not in {"captcha_answer", "captcha_token"}}
    shipment.update({"created_by_email": user["email"], "created_at": datetime.now(timezone.utc)})
    shipments_col.insert_one(shipment)
    return RedirectResponse("/my-shipments", status_code=303)


@app.post("/shipments")
async def create_shipment_json_api(request: Request, email: str = Depends(get_current_user_email)):
    if "application/json" in request.headers.get("content-type", ""):
        data = await request.json()
    else:
        data = dict(await request.form())
    data.update({"created_by_email": email, "created_at": datetime.now(timezone.utc)})
    result = shipments_col.insert_one(data)
    return JSONResponse({"id": str(result.inserted_id)}, status_code=201)


@app.get("/api/devices")
async def get_devices_api(email: str = Depends(get_current_user_email)):
    devices = list(shipments_col.find({}, {"_id": 0}))
    return {"devices": devices}


@app.get("/api/my-shipments")
async def get_my_shipments_api(email: str = Depends(get_current_user_email)):
    shipments = list(shipments_col.find({"created_by_email": email}, {"_id": 0}))
    return {"shipments": shipments}


@app.post("/api/login")
async def api_login(username: str = Form(...), password: str = Form(...)):
    email = username.strip().lower()
    user = users_col.find_one({"email": email})
    if not user or not verify_password(password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"email": user["email"], "username": user.get("username", "")})
    return {"access_token": token, "token_type": "bearer"}