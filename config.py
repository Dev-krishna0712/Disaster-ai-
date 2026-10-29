import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "disaster-ai-dev-secret-key-2026-safe-production-grade-secret")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "disaster-ai-jwt-secret-key-2026-production-ready-32bytes-long")
    JWT_ACCESS_TOKEN_EXPIRES_HOURS = 24

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'disaster_ai.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = BASE_DIR / "uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max image upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    # Data disclosure
    DATA_MODE = "DEMO/SIMULATED - Regional Geo-Climatic Baseline"
