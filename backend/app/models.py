from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Generation(Base):
    __tablename__ = "generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")  # PENDING | PROCESSING | DONE | FAILED
    prompt: Mapped[str] = mapped_column(String(2000))
    quality: Mapped[str] = mapped_column(String(10), default="480P")    # 480P | 720P
    image_url: Mapped[str] = mapped_column(String(500))
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    duration_sec: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
