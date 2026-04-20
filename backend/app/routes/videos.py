from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Generation
from app.schemas import GenerationOut, TaskStatus

router = APIRouter()

UPLOAD_DIR = Path("/uploads")


@router.get("/tasks/{generation_id}", response_model=TaskStatus)
def get_task_status(generation_id: int, db: Session = Depends(get_db)):
    gen = db.get(Generation, generation_id)
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found")
    return TaskStatus(
        id=gen.id,
        status=gen.status,
        video_url=gen.video_url,
        error_message=gen.error_message,
    )


@router.get("/videos", response_model=list[GenerationOut])
def list_videos(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return (
        db.query(Generation)
        .order_by(Generation.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/videos/{generation_id}", response_model=GenerationOut)
def get_video(generation_id: int, db: Session = Depends(get_db)):
    gen = db.get(Generation, generation_id)
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found")
    return gen


@router.delete("/videos/{generation_id}", status_code=204)
def delete_video(generation_id: int, db: Session = Depends(get_db)):
    gen = db.get(Generation, generation_id)
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found")

    # Remove local uploaded image if it exists
    if gen.image_url:
        filename = gen.image_url.rsplit("/", 1)[-1]
        local_path = UPLOAD_DIR / filename
        if local_path.exists():
            local_path.unlink(missing_ok=True)

    db.delete(gen)
    db.commit()
