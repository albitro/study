import os
from pathlib import Path


class Settings:
    # 모델 파일 경로
    MODEL_PATH: Path = Path(os.getenv("MODEL_PATH", "./models/rf_v1.joblib"))

    # 서버 정보
    APP_TITLE: str = os.getenv("APP_TITLE", "CWRU PHM Inference API")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")

    # CORS
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")


settings = Settings()
