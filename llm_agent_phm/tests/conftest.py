from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.data.loader import ANALOG_SENSORS


class FakeSensorDB:
    def __init__(self, n_samples: int = 1440):
        rng = np.random.default_rng(0)
        ts = pd.date_range("2020-06-11", periods=n_samples, freq="1min")
        data = {c: rng.normal(0, 1, n_samples) for c in ANALOG_SENSORS}
        data["label"] = np.zeros(n_samples, dtype=np.int8)
        # 마지막 100개를 fault로
        data["label"][-100:] = 1
        # fault 구간만 신호 패턴 변형
        for c in ANALOG_SENSORS:
            data[c][-100:] += rng.normal(2, 0.5, 100)
        self._df = pd.DataFrame(data, index=ts)

    @property
    def equipment_ids(self) -> list[str]:
        return ["APU-01", "APU-02", "APU-03"]

    def info(self, eid: str) -> dict:
        return {"id": eid, "name": f"{eid} 압축기", "location": "테스트랩"}

    def query(self, eid: str, start, end, sensors=None) -> pd.DataFrame:
        cols = sensors if sensors else ANALOG_SENSORS + ["label"]
        cols = [c for c in cols if c in self._df.columns]
        return self._df.loc[pd.Timestamp(start):pd.Timestamp(end), cols]


class FakeAnomalyModel:
    def score(self, X: np.ndarray) -> np.ndarray:
        return np.abs(X.mean(axis=(1, 2)))

    def per_channel_error(self, X: np.ndarray) -> np.ndarray:
        return np.abs(X.mean(axis=1))


@dataclass
class _FakeChunk:
    id: str
    text: str
    metadata: dict


@dataclass
class _FakeHit:
    chunk: _FakeChunk
    score: float


class FakeRetriever:
    def __init__(self, chunks: list[tuple[str, str, dict]]):
        self._chunks = [_FakeChunk(i, t, m) for i, t, m in chunks]

    def search(self, query: str, k: int = 3, filter_metadata: dict | None = None) -> list:
        out = []
        for c in self._chunks:
            score = sum(1 for kw in query.lower().split() if kw in c.text.lower())
            if filter_metadata and not all(c.metadata.get(k) == v for k, v in filter_metadata.items()):
                continue
            out.append(_FakeHit(c, score))
        out.sort(key=lambda h: h.score, reverse=True)
        return out[:k]


@pytest.fixture
def fake_db():
    return FakeSensorDB()


@pytest.fixture
def fake_anomaly():
    return FakeAnomalyModel()


@pytest.fixture
def fake_manual_retriever():
    return FakeRetriever([
        ("SOP-002#1", "공기 누설 발견 시 토출 밸브 O-ring 점검", {"type": "manual"}),
        ("SOP-003#2", "오일 온도 80도 초과 시 쿨러 핀 청소", {"type": "manual"}),
        ("MANUAL-001#0", "APU 정상 압력 7~9.5 bar", {"type": "manual"}),
    ])


@pytest.fixture
def fake_history_retriever():
    return FakeRetriever([
        ("INC-2020-0405", "APU-01 TP2 압력 회복 지연 Air Leak 사례",
         {"type": "history", "equipment_id": "APU-01"}),
        ("INC-2020-0607", "APU-03 토출 밸브 솔레노이드 동작 불량",
         {"type": "history", "equipment_id": "APU-03"}),
    ])


@pytest.fixture
def configured_tools(fake_db, fake_anomaly, fake_manual_retriever, fake_history_retriever):
    """ToolDeps를 주입한 상태의 tools 모듈 반환."""
    from src.agent.tools import ToolDeps, configure_tools
    configure_tools(ToolDeps(
        sensor_db=fake_db,
        anomaly_model=fake_anomaly,
        anomaly_threshold=1.0,
        anomaly_window=60,
        anomaly_stride=30,
        manual_retriever=fake_manual_retriever,
        history_retriever=fake_history_retriever,
    ))


@pytest.fixture
def fake_llm_chat():
    def _chat(messages: list[dict]) -> str:
        sys = next((m["content"] for m in messages if m["role"] == "system"), "")
        usr = next((m["content"] for m in messages if m["role"] == "user"), "")
        if "라우터" in sys or "intent" in sys:
            eid = "APU-03" if "APU-03" in usr or "3호" in usr else (
                "APU-02" if "APU-02" in usr or "2호" in usr else "APU-01"
            )
            intent = "workorder" if "작업지시서" in usr else (
                "diagnosis" if "진단" in usr or "이상" in usr else "status_check"
            )
            return (
                f'{{"intent": "{intent}", "equipment_id": "{eid}", '
                f'"needs_sensor": true, "needs_anomaly": true, '
                f'"needs_manual": {"true" if intent != "status_check" else "false"}, '
                f'"needs_history": {"true" if intent != "status_check" else "false"}}}'
            )
        if "작업지시서 입력 JSON" in sys:
            return ('{"diagnosis": "Air Leak 의심", '
                    '"recommended_actions": ["밸브 점검", "O-ring 교체"], '
                    '"priority": "HIGH", "references": ["SOP-002"]}')
        return "[가짜 진단] 정상 운전 중. 추가 조치 불필요."
    return _chat
