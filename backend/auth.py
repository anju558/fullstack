# auth.py
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from pymongo import MongoClient
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, MONGODB_URL, DB_NAME

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
client = MongoClient(MONGODB_URL)
db = client[DB_NAME]
users = db["users"]

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def get_user(email: str):
    return users.find_one({"email": email})