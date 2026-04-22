import uuid
import aiofiles

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Generation
from app.schemas import GenerationOut
from app.tasks import generate_video
from app.settings import (
    ALLOWED_UPLOAD_EXTENSIONS,
    MAX_UPLOAD_BYTES,
    STATIC_UPLOADS_URL_PREFIX,
    UPLOAD_DIR,
    BASE_URL,
)

router = APIRouter()

@router.post("/generate", response_model=GenerationOut, status_code=201)
async def create_generation(
    request: Request,
    prompt: str = Form(..., min_length=1, max_length=2000),
    quality: str = Form("480P"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if quality not in ("480P", "720P", "512P", "1024P"):
        raise HTTPException(status_code=422, detail="quality must be 480P or 720P")

    suffix = (file.filename or "").lower()
    suffix = "." + suffix.rsplit(".", 1)[-1] if "." in suffix else ""
    if suffix not in ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_UPLOAD_EXTENSIONS))}",
        )

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large")

    filename = f"{uuid.uuid4().hex}{suffix}"
    dest = UPLOAD_DIR / filename
    async with aiofiles.open(dest, "wb") as f:
        await f.write(content)

    base_url = (BASE_URL or str(request.base_url)).rstrip("/")
    image_url = f"{base_url}{STATIC_UPLOADS_URL_PREFIX}/{filename}"

    gen = Generation(prompt=prompt, quality=quality, image_url=image_url)
    db.add(gen)
    db.commit()
    db.refresh(gen)

    task = generate_video.delay(gen.id)
    gen.celery_task_id = task.id
    db.commit()
    db.refresh(gen)

    return gen
