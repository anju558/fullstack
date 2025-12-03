# main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Import backend APIRouter
# IMPORTANT: your routes.py uses "app = APIRouter()"
# so you must import it as "app", NOT "router"
from backend.routes import app as routes_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="SCMXPERTLITE",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# --------------------------
# CORS
# --------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Replace "*" with frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Static files
# --------------------------
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

# --------------------------
# Templates (HTML)
# --------------------------
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# --------------------------
# Include backend routes
# --------------------------
app.include_router(routes_router)

#uvicorn main:app --reload