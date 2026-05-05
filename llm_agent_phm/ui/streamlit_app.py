import json
import os
from datetime import date, datetime, timedelta

import httpx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")
TIMEOUT = 600 

st.set_page_config(page_title="산업 설비 LLM 에이전트", layout="wide")
st.title("🏭 산업 설비 LLM 에이전트")
st.caption(f"API: `{API_URL}`")


@st.cache_data(ttl=60)
def fetch_equipment() -> list[dict]:
    try:
        r = httpx.get(f"{API_URL}/equipment", timeout=10)
        r.raise_for_status()
        return r.json()["equipments"]
    except Exception as e:
        st.error(f"설비 목록 조회 실패: {e}")
        return []


@st.cache_data(ttl=120, show_spinner="시계열 조회 중...")
def fetch_sensors(eid: str, start: str, end: str, sensors: list[str] | None) -> dict:
    payload = {"start": start, "end": end, "sensors": sensors}
    r = httpx.post(f"{API_URL}/sensors/{eid}", json=payload, timeout=60)
    r.raise_for_status()
    return r.json()


def call_agent(query: str, eid: str | None, time_range: tuple[str, str] | None) -> dict:
    payload = {"query": query, "equipment_id": eid, "time_range": time_range, "stream": False}
    r = httpx.post(f"{API_URL}/agent/query", json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


equipments = fetch_equipment()
eid_list = [e["id"] for e in equipments] if equipments else ["APU-01", "APU-02", "APU-03"]

with st.sidebar:
    st.header("⚙️ 조회 설정")
    eid = st.selectbox("설비", eid_list, index=0)
    if equipments:
        info = next((e for e in equipments if e["id"] == eid), {})
        st.caption(f"📍 {info.get('location', '')}")

    st.markdown("---")
    st.subheader("시간 범위")

    # 테스트용 프리셋
    preset = st.radio(
        "프리셋",
        ["사용자 지정", "APU-01 정상(2/15)", "APU-02 Air Leak(5/12)", "APU-03 Air Leak(6/11)"],
        index=0,
    )
    presets = {
        "APU-01 정상(2/15)":      ("APU-01", date(2020, 2, 15), date(2020, 2, 17)),
        "APU-02 Air Leak(5/12)":  ("APU-02", date(2020, 5, 12), date(2020, 5, 14)),
        "APU-03 Air Leak(6/11)":  ("APU-03", date(2020, 6, 11), date(2020, 6, 13)),
    }
    if preset in presets:
        eid_p, d_start, d_end = presets[preset]
        eid = eid_p
        start_d = st.date_input("시작", d_start, key="ds_p")
        end_d = st.date_input("종료", d_end, key="de_p")
    else:
        start_d = st.date_input("시작", date(2020, 6, 11))
        end_d = st.date_input("종료", date(2020, 6, 13))

    sensors = st.multiselect(
        "표시할 센서",
        ["TP2", "TP3", "H1", "DV_pressure", "Reservoirs", "Oil_temperature", "Motor_current"],
        default=["TP2", "Reservoirs", "Motor_current", "Oil_temperature"],
    )

    start_iso = datetime.combine(start_d, datetime.min.time()).isoformat()
    end_iso = datetime.combine(end_d, datetime.min.time()).isoformat()

    if st.button("🔄 시계열 새로고침", use_container_width=True):
        fetch_sensors.clear()


col_chart, col_chat = st.columns([1.3, 1])

with col_chart:
    st.subheader(f"📈 {eid} 시계열")
    try:
        data = fetch_sensors(eid, start_iso, end_iso, sensors)
        st.caption(f"{data['n_samples']:,} 샘플 · {data['period']}")

        if data["points"]:
            df = pd.DataFrame([{"timestamp": p["timestamp"], **p["values"]} for p in data["points"]])
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            fig = go.Figure()
            for s in sensors:
                if s in df.columns:
                    fig.add_trace(go.Scatter(x=df["timestamp"], y=df[s], mode="lines", name=s))
            fig.update_layout(
                height=520, margin=dict(l=0, r=0, t=10, b=0),
                hovermode="x unified", legend=dict(orientation="h", y=1.05),
            )
            st.plotly_chart(fig, use_container_width=True)

            if data.get("fault_label_ratio") is not None and data["fault_label_ratio"] > 0:
                st.warning(f"⚠️ 라벨 기준 fault 구간 {data['fault_label_ratio']*100:.1f}% 포함")
        else:
            st.info("해당 구간에 데이터가 없습니다.")
    except Exception as e:
        st.error(f"시계열 조회 실패: {e}")

with col_chat:
    st.subheader("💬 에이전트와 대화")

    # 세션 메시지 저장
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 이전 대화 출력
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("trace"):
                with st.expander(f"🛠️ 호출된 노드 ({len(msg['trace'])}개)"):
                    for t in msg["trace"]:
                        st.code(f"[{t['ts']}] {t['node']}\n  {json.dumps(t.get('info', {}), ensure_ascii=False)[:200]}", language="text")
            if msg.get("workorder"):
                with st.expander("📋 작업지시서"):
                    st.markdown(msg["workorder"])
                    st.download_button(
                        "⬇️ Markdown 다운로드",
                        data=msg["workorder"],
                        file_name=f"workorder_{eid}_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                        mime="text/markdown",
                    )

    # 입력
    if prompt := st.chat_input("예: 이 설비 상태 점검하고 작업지시서 만들어줘"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("에이전트 실행 중... (LLM 호출 약 15-30초)"):
                try:
                    result = call_agent(prompt, eid, (start_iso, end_iso))
                    diagnosis = result.get("diagnosis") or "(진단 결과 없음)"
                    intent = result.get("intent", "?")

                    response = f"**Intent**: `{intent}` · **설비**: `{result.get('equipment_id') or eid}`\n\n---\n\n{diagnosis}"
                    st.markdown(response)

                    if result.get("trace"):
                        with st.expander(f"🛠️ 호출된 노드 ({len(result['trace'])}개)"):
                            for t in result["trace"]:
                                st.code(f"[{t['ts']}] {t['node']}\n  {json.dumps(t.get('info', {}), ensure_ascii=False)[:200]}", language="text")

                    if result.get("workorder"):
                        with st.expander("📋 작업지시서"):
                            st.markdown(result["workorder"])
                            st.download_button(
                                "⬇️ Markdown 다운로드",
                                data=result["workorder"],
                                file_name=f"workorder_{eid}_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                                mime="text/markdown",
                            )

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "trace": result.get("trace", []),
                        "workorder": result.get("workorder"),
                    })
                except httpx.HTTPError as e:
                    st.error(f"API 오류: {e}")

    if st.button("🗑️ 대화 초기화"):
        st.session_state.messages = []
        st.rerun()
