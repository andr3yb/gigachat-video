import os
import time
import logging
import base64
import mimetypes
from datetime import datetime, timezone
from pathlib import Path

import httpx
from celery import Task
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Generation

logger = logging.getLogger(__name__)

WAVESPEED_API_KEY = os.environ.get("WAVESPEED_API_KEY") or os.environ.get("FAL_KEY", "")
WAVESPEED_BASE_URL = os.environ.get("WAVESPEED_BASE_URL", "https://api.wavespeed.ai/api/v3")
WAVESPEED_MODEL_ID = os.environ.get(
    "WAVESPEED_MODEL_ID", "wavespeed-ai/kandinsky5-pro/image-to-video"
)
WAVESPEED_POLL_TIMEOUT_SEC = int(os.environ.get("WAVESPEED_POLL_TIMEOUT_SEC", "180"))
WAVESPEED_POLL_INTERVAL_SEC = float(os.environ.get("WAVESPEED_POLL_INTERVAL_SEC", "2"))
WAVESPEED_RESOLUTION_LOW = os.environ.get("WAVESPEED_RESOLUTION_LOW", "480p")
WAVESPEED_RESOLUTION_HIGH = os.environ.get("WAVESPEED_RESOLUTION_HIGH", "720p")
WAVESPEED_IMAGE_FIELD = os.environ.get("WAVESPEED_IMAGE_FIELD", "image")


def _get_db() -> Session:
    return SessionLocal()


def _extract_output_url(outputs: list | None) -> str:
    if not outputs:
        raise RuntimeError("WaveSpeed returned completed status with empty outputs")
    first_output = outputs[0]
    if isinstance(first_output, str):
        return first_output
    if isinstance(first_output, dict):
        for key in ("url", "video_url", "output_url"):
            value = first_output.get(key)
            if isinstance(value, str) and value:
                return value
    raise RuntimeError("WaveSpeed response outputs do not contain a valid URL")


def _build_image_input(image_url: str) -> str:
    """
    WaveSpeed can accept either public URL or base64 image.
    Localhost URLs are not reachable from WaveSpeed, so use base64 for local files.
    """
    if image_url.startswith("http://localhost") or image_url.startswith("http://127.0.0.1"):
        filename = image_url.rsplit("/", 1)[-1]
        local_path = Path("/uploads") / filename
        if not local_path.exists():
            raise RuntimeError(f"Local image not found for WaveSpeed request: {local_path}")
        binary = local_path.read_bytes()
        mime_type = mimetypes.guess_type(str(local_path))[0] or "image/jpeg"
        encoded = base64.b64encode(binary).decode("ascii")
        return f"data:{mime_type};base64,{encoded}"
    return image_url


def _call_wavespeed(image_url: str, prompt: str, quality: str) -> str:
    """Submit and poll WaveSpeed task, then return resulting video URL."""
    if not WAVESPEED_API_KEY:
        raise RuntimeError("WAVESPEED_API_KEY is empty")

    # UI keeps 512P/1024P labels, while the selected model may require other resolution tokens.
    resolution = WAVESPEED_RESOLUTION_HIGH if quality in {"1024P", "720P"} else WAVESPEED_RESOLUTION_LOW
    image_input = _build_image_input(image_url)
    headers = {
        "Authorization": f"Bearer {WAVESPEED_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prompt,
        "resolution": resolution,
        "duration": 5,
    }
    payload[WAVESPEED_IMAGE_FIELD] = image_input

    with httpx.Client(timeout=30.0) as client:
        submit_url = f"{WAVESPEED_BASE_URL}/{WAVESPEED_MODEL_ID}"
        submit_response = client.post(submit_url, headers=headers, json=payload)
        submit_response.raise_for_status()
        submit_json = submit_response.json()
        submit_data = submit_json.get("data") or {}

        task_id = submit_data.get("id")
        if not task_id:
            raise RuntimeError(f"WaveSpeed did not return task id: {submit_json}")

        result_url = ((submit_data.get("urls") or {}).get("get")) or f"{WAVESPEED_BASE_URL}/predictions/{task_id}"
        deadline = time.time() + WAVESPEED_POLL_TIMEOUT_SEC

        while time.time() < deadline:
            result_response = client.get(result_url, headers=headers)
            result_response.raise_for_status()
            result_json = result_response.json()
            data = result_json.get("data") or {}
            status = str(data.get("status", "")).lower()

            if status == "completed":
                return _extract_output_url(data.get("outputs"))
            if status == "failed":
                api_error = data.get("error") or result_json.get("message") or "WaveSpeed task failed"
                raise RuntimeError(str(api_error))
            if status not in {"created", "processing"}:
                raise RuntimeError(f"Unexpected WaveSpeed task status: {status or 'unknown'}")

            time.sleep(WAVESPEED_POLL_INTERVAL_SEC)

    raise RuntimeError("WaveSpeed task polling timeout exceeded")


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
            video_url = _call_wavespeed(gen.image_url, gen.prompt, gen.quality)
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
