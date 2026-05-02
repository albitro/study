from pydantic import BaseModel, Field, field_validator

from api.core.features import SEGMENT_LENGTH
from api.schemas.common import (
    DiagnosisOut,
    FaultFrequenciesOut,
    FeatureBlockOut,
)


class PredictRequest(BaseModel):
    signal: list[float] = Field(
        description=f"진동 신호. 필요 길이 : {SEGMENT_LENGTH} 샘플.",
        min_length=SEGMENT_LENGTH,
        max_length=SEGMENT_LENGTH,
    )
    fs: int = Field(
        default=12000,
        description="샘플링 주파수 [Hz]. CWRU는 12000.",
        gt=0,
    )
    rpm: float = Field(
        default=1772.0,
        description="회전 속도 [RPM]. 결함 주파수 계산에 사용.",
        gt=0,
    )

    @field_validator("signal")
    @classmethod
    def _check_signal_length(cls, v: list[float]) -> list[float]:
        if len(v) != SEGMENT_LENGTH:
            raise ValueError(
                f"signal length must be exactly {SEGMENT_LENGTH}, got {len(v)}"
            )
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "signal": [0.123, -0.456, 0.789, "...4093 more..."],
                "fs": 12000,
                "rpm": 1772,
            }
        }
    }


class PredictionOut(BaseModel):
    label: str = Field(description="Normal | Inner | Outer | Ball")
    class_id: int
    probabilities: dict[str, float] = Field(
        description="클래스별 예측 확률"
    )


class MetaOut(BaseModel):
    model_version: str | None = None
    inference_ms: float
    segment_length: int
    fs: int
    rpm: float


class PredictResponse(BaseModel):
    prediction: PredictionOut
    features: FeatureBlockOut
    diagnosis: DiagnosisOut
    fault_frequencies: FaultFrequenciesOut
    meta: MetaOut
