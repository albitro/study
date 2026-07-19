import json
import re
import time
from datetime import datetime
from typing import Callable

from .state import AgentState
from .tools import (
    query_sensor, detect_anomaly, search_manual, search_history, draft_workorder,
)

LLMChat = Callable[[list[dict]], str]


def _trace(node: str, info: dict) -> dict:
    return {
        "node": node,
        "ts": datetime.now().isoformat(timespec="seconds"),
        "info": info,
    }


SUPERVISOR_SYSTEM = """당신은 산업 설비 모니터링 에이전트의 라우터입니다.
사용자 자연어 요청을 분석하여 intent를 JSON으로 반환하세요.

intent 분류:
- "status_check": 단순 상태 점검/조회 ("점검", "확인", "상태", "어떤가" 등)
- "diagnosis": 이상 의심, 원인 분석 요청 ("진단", "이상", "원인", "왜")
- "workorder": 진단 + 작업지시서 필요 ("작업지시서", "조치", "고쳐", "수리")
- "general": 위 셋과 무관한 일반 질문

응답 형식 (JSON only, no extra text):
{"intent": "<intent>", "equipment_id": "<APU-01|APU-02|APU-03|null>"}

equipment_id는 사용자 발화에서 식별 가능한 경우만 채우고, 아니면 null."""


_JSON_RE = re.compile(r"\{[^{}]*\}", re.DOTALL)


def _safe_parse_json(text: str) -> dict:
    m = _JSON_RE.search(text)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {}


INTENT_NEEDS: dict[str, dict[str, bool]] = {
    "status_check": {"sensor": True,  "anomaly": True,  "manual": False, "history": False},
    "diagnosis":    {"sensor": True,  "anomaly": True,  "manual": True,  "history": True},
    "workorder":    {"sensor": True,  "anomaly": True,  "manual": True,  "history": True},
    "general":      {"sensor": False, "anomaly": False, "manual": False, "history": False},
}


def make_supervisor_node(llm_chat: LLMChat) -> Callable[[AgentState], dict]:
    def supervisor(state: AgentState) -> dict:
        t0 = time.perf_counter()
        messages = [
            {"role": "system", "content": SUPERVISOR_SYSTEM},
            {"role": "user", "content": state["query"]},
        ]
        raw = llm_chat(messages)
        parsed = _safe_parse_json(raw)
        intent = parsed.get("intent", "general")
        if intent not in INTENT_NEEDS:
            intent = "general"

        equipment_id = parsed.get("equipment_id")
        if equipment_id in ("null", "None", "", None):
            equipment_id = None
        equipment_id = state.get("equipment_id") or equipment_id

        needs = INTENT_NEEDS[intent]

        update = {
            "intent": intent,
            "equipment_id": equipment_id,
            "needs_sensor":  needs["sensor"],
            "needs_anomaly": needs["anomaly"],
            "needs_manual":  needs["manual"],
            "needs_history": needs["history"],
            "trace": [_trace("supervisor", {
                "raw": raw[:300], "parsed": parsed, "intent": intent,
                "equipment_id": equipment_id, "needs": needs,
                "elapsed": round(time.perf_counter() - t0, 3),
            })],
        }
        return update
    return supervisor


def _resolve_time_range(state: AgentState) -> tuple[str, str]:
    if state.get("time_range"):
        return state["time_range"]

    eid_to_default = {
        "APU-01": ("2020-04-12T00:00:00", "2020-04-13T00:00:00"),
        "APU-02": ("2020-05-12T00:00:00", "2020-05-13T00:00:00"),
        "APU-03": ("2020-06-11T00:00:00", "2020-06-13T00:00:00"),
    }
    eid = state.get("equipment_id") or "APU-01"
    return eid_to_default.get(eid, eid_to_default["APU-01"])


def sensor_node(state: AgentState) -> dict:
    eid = state.get("equipment_id") or "APU-01"
    start, end = _resolve_time_range(state)
    out = query_sensor.invoke({"equipment_id": eid, "start": start, "end": end})
    return {
        "sensor_summary": out,
        "trace": [_trace("sensor", {"equipment_id": eid, "start": start, "end": end})],
    }


def anomaly_node(state: AgentState) -> dict:
    eid = state.get("equipment_id") or "APU-01"
    start, end = _resolve_time_range(state)
    out = detect_anomaly.invoke({"equipment_id": eid, "start": start, "end": end})
    return {
        "anomaly_result": out,
        "trace": [_trace("anomaly", {"equipment_id": eid})],
    }


def manual_node(state: AgentState) -> dict:
    q = state["query"]
    if state.get("anomaly_result"):
        try:
            d = json.loads(state["anomaly_result"])
            if d.get("verdict") == "ANOMALY" and d.get("suspect_sensors"):
                top = ", ".join(s["sensor"] for s in d["suspect_sensors"])
                q = f"{state['query']} (의심 센서: {top})"
        except Exception:
            pass
    out = search_manual.invoke({"query": q, "k": 3})
    return {
        "manual_chunks": out,
        "trace": [_trace("manual", {"query": q})],
    }


def history_node(state: AgentState) -> dict:
    q = state["query"]
    eid = state.get("equipment_id")
    out = search_history.invoke({"query": q, "equipment_id": eid, "k": 3})
    return {
        "history_cases": out,
        "trace": [_trace("history", {"query": q, "equipment_id": eid})],
    }


SYNTHESIZER_SYSTEM = """당신은 산업 설비 진단 전문가 LLM입니다.
주어진 센서 요약, 이상 탐지 결과, 매뉴얼 발췌, 과거 사례를 종합하여 다음을 한국어로 작성하세요:

1. 현재 상태 요약 (1-2문장)
2. 진단 결론 (1문장, 가능하면 고장 유형 명시)
3. 근거 (어떤 센서/이력/매뉴얼이 결론을 뒷받침하는지)
4. 권장 다음 조치 (3개 이내 bullet)

근거 없이 추측하지 말고, 데이터가 부족하면 그렇게 명시하세요."""


def make_synthesizer_node(llm_chat: LLMChat) -> Callable[[AgentState], dict]:
    def synthesizer(state: AgentState) -> dict:
        ctx_parts = [f"[사용자 질문]\n{state['query']}"]
        if state.get("sensor_summary"):
            ctx_parts.append(f"[센서 요약]\n{state['sensor_summary']}")
        if state.get("anomaly_result"):
            ctx_parts.append(f"[이상 탐지]\n{state['anomaly_result']}")
        if state.get("manual_chunks"):
            ctx_parts.append(f"[매뉴얼 발췌]\n{state['manual_chunks']}")
        if state.get("history_cases"):
            ctx_parts.append(f"[과거 사례]\n{state['history_cases']}")

        messages = [
            {"role": "system", "content": SYNTHESIZER_SYSTEM},
            {"role": "user", "content": "\n\n".join(ctx_parts)},
        ]
        t0 = time.perf_counter()
        diagnosis = llm_chat(messages)
        return {
            "diagnosis": diagnosis,
            "trace": [_trace("synthesizer", {"elapsed": round(time.perf_counter() - t0, 3)})],
        }
    return synthesizer


WORKORDER_SYSTEM = """당신은 진단 결과를 작업지시서 입력 JSON으로 변환합니다.
다음 형식의 JSON만 반환 (다른 텍스트 금지):
{
  "diagnosis": "<한 문장 진단>",
  "recommended_actions": ["조치1", "조치2", ...],
  "priority": "LOW|MEDIUM|HIGH|EMERGENCY",
  "references": ["문서ID1", "사례ID1"]
}

판단 기준:
- 안전 위험(과열/비상정지)이면 EMERGENCY
- 운전 정지가 필요하면 HIGH
- 단순 점검/소모품 교체면 MEDIUM
- 모니터링 강화 수준이면 LOW"""


def make_workorder_node(llm_chat: LLMChat) -> Callable[[AgentState], dict]:
    def workorder_node(state: AgentState) -> dict:
        if not state.get("diagnosis"):
            return {"workorder": "(진단 결과 없음 — 작업지시서 생성 스킵)"}

        ctx = (
            f"[진단]\n{state['diagnosis']}\n\n"
            f"[참고 매뉴얼]\n{state.get('manual_chunks', '')[:1500]}\n\n"
            f"[참고 이력]\n{state.get('history_cases', '')[:1500]}"
        )
        messages = [
            {"role": "system", "content": WORKORDER_SYSTEM},
            {"role": "user", "content": ctx},
        ]
        raw = llm_chat(messages)
        parsed = _safe_parse_json(raw)
        if not parsed:
            return {
                "workorder": f"(작업지시서 JSON 파싱 실패)\nLLM 원본:\n{raw}",
                "trace": [_trace("workorder", {"error": "json_parse_fail"})],
            }

        wo_md = draft_workorder.invoke({
            "equipment_id": state.get("equipment_id") or "UNKNOWN",
            "diagnosis": parsed.get("diagnosis", state["diagnosis"][:120]),
            "recommended_actions": parsed.get("recommended_actions", []),
            "priority": parsed.get("priority", "MEDIUM"),
            "references": parsed.get("references", []),
        })
        return {
            "workorder": wo_md,
            "trace": [_trace("workorder", {"priority": parsed.get("priority")})],
        }
    return workorder_node
