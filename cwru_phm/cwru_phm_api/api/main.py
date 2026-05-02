# uvicorn api.main:app --host 0.0.0.0 --port 8000

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.core.model import load_model
from api.routers import health, predict

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Loading model from {settings.MODEL_PATH} ...")
    classifier = load_model(settings.MODEL_PATH)
    app.state.classifier = classifier
    logger.info(f"Model loaded: {classifier.meta.get('model_version')}")

    yield

    logger.info("Shutting down.")


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description=(
        "CWRU 베어링 진동 신호를 받아 베어링 상태를 분류하고 진단 근거를 반환합니다.\n\n"
        "- 입력: 4096 샘플 (12kHz @ 약 0.34초)\n"
        "- 출력: Normal / Inner / Outer / Ball + 14개 특징 + 포락선 진단\n"
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(predict.router)


@app.get("/")
def root() -> dict:
    return {
        "service": settings.APP_TITLE,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
