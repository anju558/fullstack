# config.py
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent

# MongoDB
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set in environment")

DATA_BASE = os.getenv("DATA_BASE", "scm")
USERS_COLLECTION = os.getenv("USERS_COLLECTION", "users")
SHIPMENTS_COLLECTION = os.getenv("SHIPMENTS_COLLECTION", "shipments")

# Auth
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not set")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Admin defaults
DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD")

# CAPTCHA sitekey (for frontend reCAPTCHA if used)
DATA_SITEKEY = os.getenv("DATA_SITEKEY")

# Kafka
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "device_data")
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")