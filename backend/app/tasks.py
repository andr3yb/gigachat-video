import os
import time
import logging
from datetime import datetime, timezone

import fal_client
from celery import Task
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Generation

logger = logging.getLogger(__name__)

FAL_KEY = os.environ.get("FAL_KEY", "")
os.environ["FAL_KEY"] = FAL_KEY


def _get_db() -> Session:
    return SessionLocal()


def _call_kandinsky(image_url: str, prompt: str, quality: str) -> str:
    """Call Kandinsky 5.0 via fal.ai and return video URL."""
    resolution = "1024x576" if quality == "1024P" else "512x288"

    result = fal_client.subscribe(
        "fal-ai/kling-video/v1.6/standard/image-to-video",
        arguments={
            "image_url": image_url,
            "prompt": prompt,
            "duration": "5",
            "aspect_ratio": "16:9",
        },
        with_logs=True,
    )

    video_url = result["video"]["url"]
    return video_url


class GenerateVideoTask(Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        generation_id = args[0] if args else kwargs.get("generation_id")
        if generation_id is None:
            return
        db = _get_db()
        try:
            gen = db.get(Generation, generation_id)
            if gen:
                gen.status = "FAILED"
                gen.error_message = str(exc)[:1000]
                gen.updated_at = datetime.now(timezone.utc)
                db.commit()
        finally:
            db.close()


@celery_app.task(
    bind=True,
    base=GenerateVideoTask,
    name="app.tasks.generate_video",
    max_retries=3,
    default_retry_delay=5,
)
def generate_video(self, generation_id: int):
    db = _get_db()
    try:
        gen = db.get(Generation, generation_id)
        if not gen:
            logger.error(f"Generation {generation_id} not found")
            return

        gen.status = "PROCESSING"
        gen.updated_at = datetime.now(timezone.utc)
        db.commit()

        start_time = time.time()

        try:
            video_url = _call_kandinsky(gen.image_url, gen.prompt, gen.quality)
        except Exception as exc:
            logger.warning(f"Attempt {self.request.retries + 1} failed: {exc}")
            raise self.retry(exc=exc, countdown=2 ** self.request.retries)

        duration = round(time.time() - start_time, 2)

        gen.status = "DONE"
        gen.video_url = video_url
        gen.duration_sec = duration
        gen.updated_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(f"Generation {generation_id} done in {duration}s — {video_url}")

    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()
