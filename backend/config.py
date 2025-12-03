# config.py

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent


# -----------------------------
# MongoDB Configuration
# -----------------------------
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("❌ MONGO_URI is missing in your .env file")

DATA_BASE = os.getenv("DATA_BASE", "scm")

USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")
SHIPMENTS_COLLECTION = os.getenv("SHIPMENTS_COLLECTION", "shipments")


# -----------------------------
# JWT & Authentication
# -----------------------------
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("❌ SECRET_KEY is missing in your .env file")

ALGORITHM = os.getenv("ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)


# -----------------------------
# Admin Default Credentials
# -----------------------------
DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD")


# -----------------------------
# Google reCAPTCHA
# -----------------------------
DATA_SITEKEY = os.getenv("DATA_SITEKEY")
RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY")
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")


# -----------------------------
# Kafka Configuration
# -----------------------------
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "sensor_data")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")


# -----------------------------
# Token Expiry Helper
# -----------------------------
def get_token_expiry() -> timedelta:
    return timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)


# -----------------------------
# Mail Configuration (Fixed)
# -----------------------------
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")

MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")

MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "True") == "True"
MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS", "False") == "True"
USE_CREDENTIALS = os.getenv("USE_CREDENTIALS", "True") == "True"

mail_conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_STARTTLS=MAIL_STARTTLS,
    MAIL_SSL_TLS=MAIL_SSL_TLS,
    USE_CREDENTIALS=USE_CREDENTIALS
)
