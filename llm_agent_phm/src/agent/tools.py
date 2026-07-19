import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from src.data.loader import SensorDB, ANALOG_SENSORS, make_windows
from src.rag.retriever import HybridRetriever


@dataclass
class ToolDeps:
    sensor_db: SensorDB
    anomaly_model: Any
    anomaly_threshold: float
    anomaly_window: int
    anomaly_stride: int
    manual_retriever: HybridRetriever
    history_retriever: HybridRetriever


_DEPS: ToolDeps | None = None


def configure_tools(deps: ToolDeps) -> None:
    global _DEPS
    _DEPS = deps


def _deps() -> ToolDeps:
    if _DEPS is None:
        raise RuntimeError("call configure_tools(...) first")
    return _DEPS


# -----------------------------------------------------------------------------
# 1. query_sensor
# -----------------------------------------------------------------------------

class QuerySensorInput(BaseModel):
    equipment_id: str = Field(description="설비 ID. 예: APU-01, APU-02, APU-03")
    start: str = Field(description="시작 시각 ISO 문자열. 예: '2020-06-11T00:00:00'")
    end: str = Field(description="종료 시각 ISO 문자열")
    sensors: list[str] | None = Field(
        default=None,
        description=f"조회할 센서 목록. None이면 전체. 가능: {ANALOG_SENSORS}",
    )


@tool("query_sensor", args_schema=QuerySensorInput)
def query_sensor(equipment_id: str, start: str, end: str, sensors: list[str] | None = None) -> str:
    """지정한 설비의 시간 구간 센서 데이터를 조회한다. 평균/최소/최대 통계와 샘플 수를 반환."""
    df = _deps().sensor_db.query(equipment_id, start, end, sensors)
    if df.empty:
        return json.dumps({"equipment_id": equipment_id, "n_samples": 0, "warning": "no data"}, ensure_ascii=False)
    summary = {
        "equipment_id": equipment_id,
        "period": f"{df.index.min()} ~ {df.index.max()}",
        "n_samples": int(len(df)),
        "stats": {
            c: {
                "mean": float(df[c].mean()),
                "min": float(df[c].min()),
                "max": float(df[c].max()),
                "std": float(df[c].std()),
            }
            for c in df.columns if c != "label" and pd.api.types.is_numeric_dtype(df[c])
        },
        "fault_label_ratio": float(df["label"].mean()) if "label" in df.columns else None,
    }
    return json.dumps(summary, ensure_ascii=False, indent=2)


class DetectAnomalyInput(BaseModel):
    equipment_id: str = Field(description="설비 ID")
    start: str = Field(description="시작 시각 ISO 문자열")
    end: str = Field(description="종료 시각 ISO 문자열")


@tool("detect_anomaly", args_schema=DetectAnomalyInput)
def detect_anomaly(equipment_id: str, start: str, end: str) -> str:
    """지정 구간의 이상 점수를 계산. 이상 윈도우 수, 최대 점수, 의심 센서 top3을 반환."""
    d = _deps()
    df = d.sensor_db.query(equipment_id, start, end)
    if len(df) < d.anomaly_window:
        return json.dumps({"warning": f"insufficient data: {len(df)} < window {d.anomaly_window}"}, ensure_ascii=False)

    X, _ = make_windows(df, window=d.anomaly_window, stride=d.anomaly_stride)
    scores = d.anomaly_model.score(X)
    above = scores > d.anomaly_threshold

    out: dict = {
        "equipment_id": equipment_id,
        "period": f"{df.index.min()} ~ {df.index.max()}",
        "n_windows": int(len(scores)),
        "n_anomaly": int(above.sum()),
        "anomaly_ratio": float(above.mean()),
        "max_score": float(scores.max()),
        "threshold": float(d.anomaly_threshold),
        "verdict": "ANOMALY" if above.sum() > 0 else "NORMAL",
    }
    # AE 모델일 때만 채널별 오차 → 의심 센서 식별
    if hasattr(d.anomaly_model, "per_channel_error"):
        per_ch = d.anomaly_model.per_channel_error(X)  # (N, C)
        # 이상 윈도우 평균
        if above.sum() > 0:
            mean_err = per_ch[above].mean(axis=0)
        else:
            mean_err = per_ch.mean(axis=0)
        order = np.argsort(mean_err)[::-1][:3]
        out["suspect_sensors"] = [
            {"sensor": ANALOG_SENSORS[i], "error": float(mean_err[i])} for i in order
        ]
    return json.dumps(out, ensure_ascii=False, indent=2)


class SearchManualInput(BaseModel):
    query: str = Field(description="자연어 검색 쿼리. 예: '공기 누설 발견 시 점검 절차'")
    k: int = Field(default=3, description="반환할 청크 수")


@tool("search_manual", args_schema=SearchManualInput)
def search_manual(query: str, k: int = 3) -> str:
    """매뉴얼/SOP 문서에서 관련 청크를 검색."""
    hits = _deps().manual_retriever.search(query, k=k)
    out = [
        {
            "id": h.chunk.id,
            "source": h.chunk.metadata.get("source"),
            "title": h.chunk.metadata.get("title"),
            "score": round(h.score, 4),
            "text": h.chunk.text,
        }
        for h in hits
    ]
    return json.dumps(out, ensure_ascii=False, indent=2)


class SearchHistoryInput(BaseModel):
    query: str = Field(description="증상 키워드. 예: 'TP2 압력 저하 + 모터 전류 증가'")
    equipment_id: str | None = Field(default=None, description="특정 설비로 필터 (선택)")
    k: int = Field(default=3, description="반환할 사례 수")


@tool("search_history", args_schema=SearchHistoryInput)
def search_history(query: str, equipment_id: str | None = None, k: int = 3) -> str:
    """과거 고장 이력에서 유사 사례를 검색."""
    filt = {"equipment_id": equipment_id} if equipment_id else None
    hits = _deps().history_retriever.search(query, k=k, filter_metadata=filt)
    out = [
        {
            "case_id": h.chunk.id,
            "score": round(h.score, 4),
            "metadata": h.chunk.metadata,
            "text": h.chunk.text,
        }
        for h in hits
    ]
    return json.dumps(out, ensure_ascii=False, indent=2)


class DraftWorkorderInput(BaseModel):
    equipment_id: str
    diagnosis: str = Field(description="진단 결론. 예: 'Air Leak (DV O-ring 노후)'")
    recommended_actions: list[str] = Field(description="조치 항목 리스트")
    priority: str = Field(default="MEDIUM", description="LOW | MEDIUM | HIGH | EMERGENCY")
    references: list[str] = Field(default_factory=list, description="참조 문서 ID")


@tool("draft_workorder", args_schema=DraftWorkorderInput)
def draft_workorder(
    equipment_id: str,
    diagnosis: str,
    recommended_actions: list[str],
    priority: str = "MEDIUM",
    references: list[str] | None = None,
) -> str:
    """작업지시서 초안을 Markdown 형식으로 생성."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    refs = references or []
    ref_block = "\n".join(f"- {r}" for r in refs) if refs else "- (없음)"
    actions_block = "\n".join(f"{i+1}. {a}" for i, a in enumerate(recommended_actions))
    md = f"""# 작업지시서 (초안)

| 항목 | 내용 |
|------|------|
| 발급 시각 | {now} |
| 설비 ID | {equipment_id} |
| 우선순위 | **{priority}** |
| 진단 | {diagnosis} |

## 권장 조치
{actions_block}

## 참조 문서
{ref_block}

## 비고
- 본 지시서는 LLM 에이전트가 자동 생성한 초안이며, 작업 전 반드시 담당자 검토 필요.
"""
    return md


ALL_TOOLS = [query_sensor, detect_anomaly, search_manual, search_history, draft_workorder]
