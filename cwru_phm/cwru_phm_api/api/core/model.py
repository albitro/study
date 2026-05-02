import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import joblib
import numpy as np

from api.core.diagnosis import DiagnosisInfo, diagnose
from api.core.fault_freq import FaultFrequencies, compute_fault_frequencies
from api.core.features import (
    FEATURE_NAMES,
    SEGMENT_LENGTH,
    FeatureBlock,
    extract_features,
)


@dataclass
class PredictionResult:
    label: str                      # 'Normal' | 'Inner' | 'Outer' | 'Ball'
    class_id: int
    probabilities: dict[str, float] # {'Normal': 0.02, 'Inner': 0.05, ...}
    features: FeatureBlock
    diagnosis: DiagnosisInfo
    fault_freq: FaultFrequencies
    inference_ms: float


class FaultClassifier:
    def __init__(self, model_path: Path):
        self.model_path = Path(model_path)
        self.meta_path = self.model_path.with_suffix(".meta.json")

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {self.model_path}\n"
                f"먼저 'python scripts/train.py'를 실행하여 모델을 만들어주세요."
            )

        # 모델 로드
        self.model = joblib.load(self.model_path)

        # 메타데이터 로드 (없으면 기본값)
        if self.meta_path.exists():
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.meta = json.load(f)
        else:
            self.meta = {
                "model_version": self.model_path.stem,
                "feature_names": FEATURE_NAMES,
                "class_names": ["Normal", "Inner", "Outer", "Ball"],
                "fs": 12000,
                "segment_length": SEGMENT_LENGTH,
            }

        self.class_names: list[str] = self.meta.get(
            "class_names", ["Normal", "Inner", "Outer", "Ball"]
        )
        self.feature_names: list[str] = self.meta.get("feature_names", FEATURE_NAMES)

        # 학습 시 특징 순서가 현재 코드와 일치하는지 확인
        if self.feature_names != FEATURE_NAMES:
            raise RuntimeError(
                "모델의 feature 순서가 현재 코드와 일치하지 않습니다. "
                "모델을 재학습해주세요."
            )

    def predict(
        self,
        signal_arr: np.ndarray,
        fs: int,
        rpm: float,
    ) -> PredictionResult:
        t0 = time.perf_counter()

        # 결함 주파수 계산
        ff = compute_fault_frequencies(rpm)

        # 14개 특징 추출
        feats = extract_features(signal_arr, fs=fs, fault_freq=ff)

        # 모델 추론
        feature_vec = feats.to_vector().reshape(1, -1)
        class_id = int(self.model.predict(feature_vec)[0])
        probs_arr = self.model.predict_proba(feature_vec)[0]
        probabilities = {
            name: float(p) for name, p in zip(self.class_names, probs_arr)
        }

        # 진단 근거
        info = diagnose(signal_arr, fs=fs, fault_freq=ff)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        return PredictionResult(
            label=self.class_names[class_id],
            class_id=class_id,
            probabilities=probabilities,
            features=feats,
            diagnosis=info,
            fault_freq=ff,
            inference_ms=elapsed_ms,
        )

    def info(self) -> dict:
        """모델 정보. /model/info 엔드포인트에서 그대로 반환."""
        return {
            "model_version": self.meta.get("model_version"),
            "trained_at": self.meta.get("trained_at"),
            "trained_rpm": self.meta.get("trained_rpm"),
            "fs": self.meta.get("fs"),
            "segment_length": self.meta.get("segment_length"),
            "class_names": self.class_names,
            "feature_names": self.feature_names,
            "metrics": self.meta.get("metrics", {}),
        }


_classifier: Optional[FaultClassifier] = None


def load_model(model_path: Path) -> FaultClassifier:
    global _classifier
    _classifier = FaultClassifier(model_path)
    return _classifier


def get_classifier() -> FaultClassifier:
    if _classifier is None:
        raise RuntimeError(
            "Model is not loaded. Call load_model() first (보통 lifespan에서)."
        )
    return _classifier
