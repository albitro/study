from typing import Any, Literal

from pydantic import BaseModel, Field


class AgentQueryRequest(BaseModel):
    query: str = Field(description="자연어 사용자 질문")
    equipment_id: str | None = Field(
        default=None,
        description="설비 ID 힌트. 미지정 시 LLM이 query에서 추출 시도. 예: APU-01",
    )
    time_range: tuple[str, str] | None = Field(
        default=None,
        description="(start, end) ISO 문자열 튜플. 미지정 시 테스트 디폴트 사용.",
    )
    stream: bool = Field(default=False, description="True면 SSE 스트리밍 응답")


class TraceEvent(BaseModel):
    node: str
    ts: str
    info: dict[str, Any] = {}


class AgentQueryResponse(BaseModel):
    intent: str | None = None
    equipment_id: str | None = None
    diagnosis: str | None = None
    workorder: str | None = None
    sensor_summary: str | None = None
    anomaly_result: str | None = None
    manual_chunks: str | None = None
    history_cases: str | None = None
    trace: list[TraceEvent] = []


class SensorQueryRequest(BaseModel):
    start: str
    end: str
    sensors: list[str] | None = None


class SensorPoint(BaseModel):
    timestamp: str
    values: dict[str, float]


class SensorQueryResponse(BaseModel):
    equipment_id: str
    n_samples: int
    period: str
    points: list[SensorPoint] = []
    fault_label_ratio: float | None = None


class EquipmentInfo(BaseModel):
    id: str
    name: str
    location: str


class EquipmentListResponse(BaseModel):
    equipments: list[EquipmentInfo]


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    model_loaded: bool
    agent_loaded: bool
    rag_loaded: bool
    version: str
