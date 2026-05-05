from typing import Callable

from langgraph.graph import StateGraph, START, END

from .state import AgentState
from .nodes import (
    LLMChat,
    make_supervisor_node,
    make_synthesizer_node,
    make_workorder_node,
    sensor_node, anomaly_node, manual_node, history_node,
)


def _route_after_supervisor(state: AgentState) -> list[str]:
    targets: list[str] = []
    if state.get("needs_sensor"):
        targets.append("sensor")
    if state.get("needs_anomaly"):
        targets.append("anomaly")
    if state.get("needs_manual"):
        targets.append("manual")
    if state.get("needs_history"):
        targets.append("history")
    return targets or ["synthesizer"]


def _route_after_synth(state: AgentState) -> str:
    return "workorder" if state.get("intent") == "workorder" else END


def build_agent(llm_chat: LLMChat) -> Callable:
    g = StateGraph(AgentState)

    g.add_node("supervisor", make_supervisor_node(llm_chat))
    g.add_node("sensor", sensor_node)
    g.add_node("anomaly", anomaly_node)
    g.add_node("manual", manual_node)
    g.add_node("history", history_node)
    g.add_node("synthesizer", make_synthesizer_node(llm_chat))
    g.add_node("workorder", make_workorder_node(llm_chat))

    g.add_edge(START, "supervisor")
    g.add_conditional_edges(
        "supervisor",
        _route_after_supervisor,
        {"sensor": "sensor", "anomaly": "anomaly", "manual": "manual",
         "history": "history", "synthesizer": "synthesizer"},
    )

    for n in ("sensor", "anomaly", "manual", "history"):
        g.add_edge(n, "synthesizer")

    g.add_conditional_edges(
        "synthesizer",
        _route_after_synth,
        {"workorder": "workorder", END: END},
    )
    g.add_edge("workorder", END)

    return g.compile()
