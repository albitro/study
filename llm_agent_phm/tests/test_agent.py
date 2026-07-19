from src.agent.graph import build_agent


def _run(agent, query: str, eid: str = None, time_range: tuple = None) -> dict:
    init = {"query": query, "equipment_id": eid, "time_range": time_range, "trace": []}
    return agent.invoke(init)


def test_status_check_runs_sensor_and_anomaly_only(configured_tools, fake_llm_chat):
    agent = build_agent(fake_llm_chat)
    final = _run(
        agent,
        "1호 압축기 6월 11일 상태 점검해줘",
        eid="APU-01",
        time_range=("2020-06-11T00:00:00", "2020-06-11T05:00:00"),
    )
    assert final["intent"] == "status_check"
    assert final["sensor_summary"] is not None
    assert final["anomaly_result"] is not None
    # status_check면 manual/history 호출 안 함
    assert final.get("manual_chunks") is None
    assert final.get("history_cases") is None
    # workorder는 만들지 않음
    assert final.get("workorder") in (None, "")


def test_diagnosis_runs_full_pipeline_no_workorder(configured_tools, fake_llm_chat):
    agent = build_agent(fake_llm_chat)
    final = _run(
        agent,
        "3호 압축기 압력이 이상한데 진단해줘",
        eid="APU-03",
        time_range=("2020-06-11T22:00:00", "2020-06-11T23:59:00"),
    )
    assert final["intent"] == "diagnosis"
    assert final["sensor_summary"] is not None
    assert final["anomaly_result"] is not None
    assert final["manual_chunks"] is not None
    assert final["history_cases"] is not None
    assert final["diagnosis"] is not None
    assert final.get("workorder") in (None, "")


def test_workorder_intent_produces_markdown(configured_tools, fake_llm_chat):
    agent = build_agent(fake_llm_chat)
    final = _run(
        agent,
        "2호 누설 의심, 작업지시서 만들어줘",
        eid="APU-02",
        time_range=("2020-06-11T22:00:00", "2020-06-11T23:59:00"),
    )
    assert final["intent"] == "workorder"
    assert final["workorder"] is not None
    assert "# 작업지시서" in final["workorder"]
    assert "APU-02" in final["workorder"]


def test_trace_records_each_node(configured_tools, fake_llm_chat):
    agent = build_agent(fake_llm_chat)
    final = _run(
        agent,
        "3호 압축기 진단",
        eid="APU-03",
        time_range=("2020-06-11T22:00:00", "2020-06-11T23:59:00"),
    )
    nodes_called = {t["node"] for t in final["trace"]}
    assert "supervisor" in nodes_called
    assert "synthesizer" in nodes_called
    # diagnosis intent → 적어도 sensor + anomaly 노드 trace
    assert "sensor" in nodes_called
    assert "anomaly" in nodes_called


def test_equipment_id_inferred_from_query(configured_tools, fake_llm_chat):
    """query에 'APU-03' 들어있으면 supervisor가 추출."""
    agent = build_agent(fake_llm_chat)
    final = _run(
        agent,
        "APU-03 진단",
        time_range=("2020-06-11T22:00:00", "2020-06-11T23:59:00"),
    )
    assert final["equipment_id"] == "APU-03"
