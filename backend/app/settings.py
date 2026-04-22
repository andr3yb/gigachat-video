import os
from pathlib import Path


def _env(name: str, default: str) -> str:
    value = os.environ.get(name)
    return value if value not in (None, "") else default


# === Core URLs ===
# If BASE_URL is empty, backend will use request.host when building image_url.
BASE_URL = os.environ.get("BASE_URL", "")

# === Storage / uploads ===
UPLOAD_DIR = Path(_env("UPLOAD_DIR", "/uploads"))
STATIC_UPLOADS_URL_PREFIX = _env("STATIC_UPLOADS_URL_PREFIX", "/static/uploads")

# Comma-separated file extensions: ".jpg,.jpeg,.png,.webp"
ALLOWED_UPLOAD_EXTENSIONS = {
    ext.strip().lower()
    for ext in _env("ALLOWED_UPLOAD_EXTENSIONS", ".jpg,.jpeg,.png,.webp").split(",")
    if ext.strip()
}

MAX_UPLOAD_MB = int(_env("MAX_UPLOAD_MB", "20"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

# === Database / Redis ===
DATABASE_URL = os.environ.get("DATABASE_URL", "")
REDIS_URL = _env("REDIS_URL", "redis://redis:6379/0")

# === WaveSpeed ===
WAVESPEED_API_KEY = os.environ.get("WAVESPEED_API_KEY", "")
WAVESPEED_BASE_URL = _env("WAVESPEED_BASE_URL", "https://api.wavespeed.ai/api/v3")
WAVESPEED_MODEL_ID = _env("WAVESPEED_MODEL_ID", "wavespeed-ai/wan-2.2-spicy/image-to-video")
WAVESPEED_POLL_TIMEOUT_SEC = int(_env("WAVESPEED_POLL_TIMEOUT_SEC", "180"))
WAVESPEED_POLL_INTERVAL_SEC = float(_env("WAVESPEED_POLL_INTERVAL_SEC", "2"))
WAVESPEED_RESOLUTION_LOW = _env("WAVESPEED_RESOLUTION_LOW", "480p")
WAVESPEED_RESOLUTION_HIGH = _env("WAVESPEED_RESOLUTION_HIGH", "720p")
WAVESPEED_IMAGE_FIELD = _env("WAVESPEED_IMAGE_FIELD", "image")

