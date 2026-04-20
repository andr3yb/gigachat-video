from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class GenerationCreate(BaseModel):
    prompt: str
    quality: str = "480P"


class GenerationOut(BaseModel):
    id: int
    status: str
    prompt: str
    quality: str
    image_url: str
    video_url: Optional[str]
    error_message: Optional[str]
    duration_sec: Optional[float]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskStatus(BaseModel):
    id: int
    status: str
    video_url: Optional[str]
    error_message: Optional[str]
