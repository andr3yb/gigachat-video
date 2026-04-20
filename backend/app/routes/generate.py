import os
import uuid
import aiofiles
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Generation
from app.schemas import GenerationOut
from app.tasks import generate_video

router = APIRouter()

UPLOAD_DIR = Path("/uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/generate", response_model=GenerationOut, status_code=201)
async def create_generation(
    prompt: str = Form(..., min_length=1, max_length=2000),
    quality: str = Form("512P"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if quality not in ("512P", "1024P"):
        raise HTTPException(status_code=422, detail="quality must be 512P or 1024P")

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 20 MB)")

    filename = f"{uuid.uuid4().hex}{suffix}"
    dest = UPLOAD_DIR / filename
    async with aiofiles.open(dest, "wb") as f:
        await f.write(content)

    base_url = os.environ.get("BASE_URL", "http://localhost")
    image_url = f"{base_url}/static/uploads/{filename}"

    gen = Generation(prompt=prompt, quality=quality, image_url=image_url)
    db.add(gen)
    db.commit()
    db.refresh(gen)

    task = generate_video.delay(gen.id)
    gen.celery_task_id = task.id
    db.commit()
    db.refresh(gen)

    return gen
