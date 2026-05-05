import asyncio
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from src.agent.graph import build_agent
from src.agent.tools import ToolDeps, configure_tools
from src.api.schemas import (
    AgentQueryRequest, AgentQueryResponse, TraceEvent,
    SensorQueryRequest, SensorQueryResponse, SensorPoint,
    EquipmentInfo, EquipmentListResponse,
    HealthResponse,
)
from src.data.loader import SensorDB, load_metropt3, EQUIPMENT_REGISTRY
from src.models.anomaly import AEAnomalyModel
from src.models.llm import LLMConfig, chat, load_hf_model
from src.rag.retriever import load_retriever


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data" / "metropt3"))
ARTIFACTS = Path(os.getenv("ARTIFACTS_DIR", PROJECT_ROOT / "models_artifacts"))
LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "Qwen/Qwen2.5-7B-Instruct")
LLM_QUANT = os.getenv("LLM_QUANT", "int4")
APP_VERSION = "0.1.0"


class _State:
    db: SensorDB | None = None
    agent = None
    model = None
    tokenizer = None
    rag_loaded: bool = False


state = _State()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[lifespan] loading data from {DATA_DIR}")
    df = load_metropt3(data_dir=DATA_DIR)
    state.db = SensorDB(df=df)
    print(f"[lifespan] data loaded: {df.shape}")

    print(f"[lifespan] loading anomaly model from {ARTIFACTS}")
    ae = AEAnomalyModel.load(ARTIFACTS / "convae_v1.pt", device="cpu")
    meta = json.loads((ARTIFACTS / "anomaly_meta.json").read_text(encoding="utf-8"))

    print(f"[lifespan] loading RAG retrievers")
    manual_r = load_retriever(ARTIFACTS / "rag" / "manual")
    history_r = load_retriever(ARTIFACTS / "rag" / "history")
    state.rag_loaded = True

    configure_tools(ToolDeps(
        sensor_db=state.db,
        anomaly_model=ae,
        anomaly_threshold=meta["convae"]["threshold"],
        anomaly_window=meta["window"],
        anomaly_stride=meta["stride"],
        manual_retriever=manual_r,
        history_retriever=history_r,
    ))

    print(f"[lifespan] loading LLM: {LLM_MODEL_ID} ({LLM_QUANT})")
    llm_cfg = LLMConfig(model_id=LLM_MODEL_ID, quantization=LLM_QUANT)
    state.model, state.tokenizer = load_hf_model(llm_cfg)

    def _llm_chat(messages):
        return chat(messages, state.model, state.tokenizer, max_new_tokens=512, temperature=0.2)

    state.agent = build_agent(_llm_chat)
    print("[lifespan] agent compiled. ready.")

    yield

    print("[lifespan] shutdown")


app = FastAPI(
    title="Industrial Equipment LLM Agent API",
    version=APP_VERSION,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok" if state.agent is not None else "degraded",
        model_loaded=state.model is not None,
        agent_loaded=state.agent is not None,
        rag_loaded=state.rag_loaded,
        version=APP_VERSION,
    )


@app.get("/equipment", response_model=EquipmentListResponse)
def list_equipment():
    return EquipmentListResponse(equipments=[
        EquipmentInfo(id=k, name=v["name"], location=v["location"])
        for k, v in EQUIPMENT_REGISTRY.items()
    ])


@app.post("/sensors/{equipment_id}", response_model=SensorQueryResponse)
def query_sensors(equipment_id: str, req: SensorQueryRequest):
    if state.db is None:
        raise HTTPException(503, "sensor DB not loaded")
    try:
        df = state.db.query(equipment_id, req.start, req.end, req.sensors)
    except KeyError:
        raise HTTPException(404, f"unknown equipment: {equipment_id}")

    sensor_cols = [c for c in df.columns if c != "label" and pd.api.types.is_numeric_dtype(df[c])]
    points = [
        SensorPoint(
            timestamp=ts.isoformat(),
            values={c: float(row[c]) for c in sensor_cols},
        )
        for ts, row in df.iterrows()
    ]
    return SensorQueryResponse(
        equipment_id=equipment_id,
        n_samples=len(df),
        period=f"{df.index.min()} ~ {df.index.max()}" if len(df) else "",
        points=points,
        fault_label_ratio=float(df["label"].mean()) if "label" in df.columns and len(df) else None,
    )


@app.post("/agent/query")
async def agent_query(req: AgentQueryRequest):
    if state.agent is None:
        raise HTTPException(503, "agent not loaded")

    init_state = {
        "query": req.query,
        "equipment_id": req.equipment_id,
        "time_range": req.time_range,
        "trace": [],
    }

    if not req.stream:
        final = await asyncio.to_thread(state.agent.invoke, init_state)
        return _to_response(final)

    async def event_gen():
        try:
            async for event in state.agent.astream(init_state):
                payload = json.dumps({"event": event}, ensure_ascii=False, default=str)
                yield f"data: {payload}\n\n"
        except Exception as e:
            err = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"data: {err}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")


def _to_response(final: dict) -> AgentQueryResponse:
    return AgentQueryResponse(
        intent=final.get("intent"),
        equipment_id=final.get("equipment_id"),
        diagnosis=final.get("diagnosis"),
        workorder=final.get("workorder"),
        sensor_summary=final.get("sensor_summary"),
        anomaly_result=final.get("anomaly_result"),
        manual_chunks=final.get("manual_chunks"),
        history_cases=final.get("history_cases"),
        trace=[TraceEvent(**t) for t in final.get("trace", [])],
    )


@app.get("/")
def root():
    return {
        "name": "Industrial Equipment LLM Agent",
        "version": APP_VERSION,
        "docs": "/docs",
        "endpoints": ["/health", "/equipment", "/sensors/{eid}", "/agent/query"],
    }
