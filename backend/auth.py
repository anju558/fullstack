# auth.py  —  Enterprise-grade secure version

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv
import logging

# ----------------------------------------------------
# Load .env variables
# ----------------------------------------------------
load_dotenv()

# ----------------------------------------------------
# Logger setup
# ----------------------------------------------------
logger = logging.getLogger("auth")
logger.setLevel(logging.INFO)

# ----------------------------------------------------
# JWT Configuration (secure defaults + env overrides)
# ----------------------------------------------------


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "4e5f2a6b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f")              # fallback for dev
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))

# ----------------------------------------------------
# Password hashing
# ----------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 token extractor (for API routes)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


# =====================================================================================
# PASSWORD UTILITIES
# =====================================================================================
def get_password_hash(password: str) -> str:
    """Hash password with bcrypt."""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal error while securing password."
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify hashed password."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False  # never raise — prevents leaking details


# =====================================================================================
# JWT TOKEN UTILITIES
# =====================================================================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token.
    Payload **must include 'email'** for authentication.
    """
    try:
        to_encode = data.copy()

        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})

        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return token

    except Exception as e:
        logger.error(f"Token creation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal error while creating authentication token."
        )


# =====================================================================================
# TOKEN VERIFICATION (used by API /profile-data etc.)
# =====================================================================================
def get_current_user_email(token: str = Depends(oauth2_scheme)) -> str:
    """
    Validate JWT token extracted from Authorization header.
    Returns: email string
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")

        if not email:
            logger.warning("Token validation failed: no email in payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token.",
            )

        return email

    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
        )
    except Exception as e:
        logger.error(f"Unexpected token validation error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal error while validating token."
        )


# =====================================================================================
# BACKWARD COMPATIBILITY LAYER
# =====================================================================================
def verify_token(token: str = Depends(oauth2_scheme)) -> str:
    """
    Deprecated alias — kept for backward compatibility.
    """
    return get_current_user_email(token)
