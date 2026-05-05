import json

import pytest

from src.agent.tools import (
    query_sensor, detect_anomaly, search_manual, search_history, draft_workorder,
)


def test_query_sensor_returns_summary(configured_tools):
    out = query_sensor.invoke({
        "equipment_id": "APU-01",
        "start": "2020-06-11T00:00:00",
        "end": "2020-06-11T03:00:00",
        "sensors": ["TP2", "Motor_current"],
    })
    data = json.loads(out)
    assert data["equipment_id"] == "APU-01"
    assert data["n_samples"] > 0
    assert "TP2" in data["stats"]
    assert {"mean", "min", "max", "std"} <= set(data["stats"]["TP2"].keys())


def test_query_sensor_no_data(configured_tools):
    out = query_sensor.invoke({
        "equipment_id": "APU-01",
        "start": "2030-01-01T00:00:00",
        "end": "2030-01-02T00:00:00",
    })
    data = json.loads(out)
    assert data["n_samples"] == 0


def test_detect_anomaly_normal_segment(configured_tools):
    out = detect_anomaly.invoke({
        "equipment_id": "APU-01",
        "start": "2020-06-11T00:00:00",
        "end": "2020-06-11T05:00:00",
    })
    data = json.loads(out)
    assert "verdict" in data
    assert data["n_windows"] >= 1


def test_detect_anomaly_fault_segment_includes_suspect(configured_tools):
    out = detect_anomaly.invoke({
        "equipment_id": "APU-01",
        "start": "2020-06-11T22:00:00",
        "end": "2020-06-11T23:59:00",
    })
    data = json.loads(out)
    assert "suspect_sensors" in data
    assert len(data["suspect_sensors"]) == 3
    for s in data["suspect_sensors"]:
        assert "sensor" in s and "error" in s


def test_search_manual_returns_top_k(configured_tools):
    out = search_manual.invoke({"query": "공기 누설 점검", "k": 2})
    data = json.loads(out)
    assert isinstance(data, list)
    assert len(data) <= 2
    if data:
        assert {"id", "score", "text"} <= set(data[0].keys())


def test_search_history_filter_by_equipment(configured_tools):
    out = search_history.invoke({
        "query": "압력 이상",
        "equipment_id": "APU-03",
        "k": 3,
    })
    data = json.loads(out)
    for case in data:
        assert case["metadata"].get("equipment_id") == "APU-03"


def test_draft_workorder_format():
    md = draft_workorder.invoke({
        "equipment_id": "APU-02",
        "diagnosis": "Air Leak (DV O-ring 노후)",
        "recommended_actions": ["O-ring 교체", "30분 무부하 시험"],
        "priority": "HIGH",
        "references": ["SOP-002"],
    })
    assert "# 작업지시서" in md
    assert "APU-02" in md
    assert "**HIGH**" in md
    assert "O-ring 교체" in md
    assert "SOP-002" in md


def test_tools_require_configuration():
    from src.agent import tools as tmod
    saved = tmod._DEPS
    tmod._DEPS = None
    try:
        with pytest.raises(RuntimeError):
            query_sensor.invoke({"equipment_id": "APU-01", "start": "2020-01-01", "end": "2020-01-02"})
    finally:
        tmod._DEPS = saved
