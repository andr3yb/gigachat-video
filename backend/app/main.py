from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routes.generate import router as generate_router
from app.routes.videos import router as videos_router
from app.settings import UPLOAD_DIR, STATIC_UPLOADS_URL_PREFIX


@asynccontextmanager
async def lifespan(app: FastAPI):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    init_db()
    yield


app = FastAPI(title="AI Video Factory", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(STATIC_UPLOADS_URL_PREFIX, StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

app.include_router(generate_router, prefix="/api")
app.include_router(videos_router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
