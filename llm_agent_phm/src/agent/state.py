from typing import Annotated, TypedDict, Literal
from operator import add


# Intent 분류
Intent = Literal["status_check", "diagnosis", "workorder", "general"]


class AgentState(TypedDict, total=False):
    # 입력
    query: str
    equipment_id: str | None
    time_range: tuple[str, str] | None

    # supervisor 결정
    intent: Intent
    needs_sensor: bool
    needs_anomaly: bool
    needs_manual: bool
    needs_history: bool

    # tool 호출 결과
    sensor_summary: str | None
    anomaly_result: str | None
    manual_chunks: str | None
    history_cases: str | None

    # 최종 산출물
    diagnosis: str | None
    workorder: str | None

    # 디버그 trace
    trace: Annotated[list[dict], add]
