# 산업 설비 LLM 에이전트

> **Qwen2.5-7B-Instruct + LangGraph** 기반의 멀티스텝 에이전트로, 공장 설비의 이상 탐지부터 작업지시서 자동 생성까지 자율적으로 수행하는 프로젝트
> RTX 4060 (8GB VRAM) 환경에서 INT4 양자화로 로컬 추론

---

## 프로젝트 개요

기존 [`llm_phm/`](../llm_phm) 프로젝트는 "질문 → 검색 → 답변"의 단순 1턴 RAG 파이프라인이었습니다. 본 프로젝트는 **Agentic AI**(멀티스텝 추론, 도구 호출, 조건부 분기)를 LangGraph로 구현하여, 산업 현장의 실제 의사결정 흐름을 모사합니다.

사용자가 자연어로 "3호 압축기 압력이 이상한데 작업지시서 만들어줘"라고 요청하면, 에이전트는 다음 단계를 자율적으로 수행합니다.

1. 사용자 의도(intent)를 파악하여 어떤 도구를 호출할지 결정
2. 시계열 센서 데이터 조회 + ConvAE 이상 탐지를 병렬 수행
3. 매뉴얼/SOP RAG 검색과 과거 고장 이력 검색을 병렬 수행
4. 모든 결과를 종합하여 진단 보고서 작성
5. (필요 시) 작업지시서 Markdown 자동 생성

---

## 사용 환경


| 항목   | 사양                         |
| -------- | ------------------------------ |
| GPU    | NVIDIA RTX 4060 (8GB VRAM)   |
| RAM    | 64GB                         |
| OS     | Windows 11 / WSL2 (Docker용) |
| Python | 3.11                         |
| CUDA   | 12.4 (Docker), 12.8 (호스트) |

---

## 모델 선정 근거

### 왜 Qwen2.5-7B-Instruct + INT4 양자화인가

기존 `llm_phm/`에서 사용한 Qwen2.5-3B는 단순 답변 생성에는 충분했지만, **멀티스텝 에이전트의 supervisor 라우팅(JSON 출력 정확도)** 과 **종합 진단 보고서 작성(컨텍스트 융합 능력)** 에서 한계를 보였습니다.


| 모델                  | FP16 VRAM | INT4 VRAM  | 8GB 동작 | tool-calling 품질 |
| ----------------------- | ----------- | ------------ | ---------- | ------------------- |
| Qwen2.5-3B            | ~6GB      | ~2GB       | 안정     | 보통              |
| **Qwen2.5-7B + INT4** | ~17GB     | **~5.5GB** | **안정** | **우수**          |
| Qwen2.5-7B FP16       | ~17GB     | -          | 불가     | -                 |

INT4 양자화(bitsandbytes nf4)를 적용하면 7B 모델을 8GB VRAM 내에서 안정적으로 운용 가능하며, supervisor의 JSON intent 분류 정확도와 synthesizer의 한국어 보고서 품질이 3B 대비 명확히 향상됩니다.

---

## 아키텍처

```
사용자 질문
   ↓
[supervisor]   ─ intent 분류 (status_check / diagnosis / workorder / general)
   ↓ (조건부 병렬)
[sensor]       ─ MetroPT-3 가상 멀티 설비 시계열 조회
[anomaly]      ─ ConvAE 재구성 오차 기반 이상 탐지 + 의심 센서 식별
[manual]       ─ SOP/매뉴얼 FAISS RAG 검색
[history]      ─ 과거 고장 이력 FAISS RAG 검색
   ↓
[synthesizer]  ─ 모든 결과를 종합한 진단 보고서
   ↓ (intent == workorder인 경우)
[workorder]    ─ 작업지시서 Markdown 자동 생성
```


| 구성요소            | 기술 스택                                                                |
| --------------------- | -------------------------------------------------------------------------- |
| 에이전트 프레임워크 | **LangGraph** (StateGraph)                                               |
| LLM                 | Qwen2.5-7B-Instruct (INT4 양자화)                                        |
| 임베딩 모델         | `paraphrase-multilingual-MiniLM-L12-v2`                                  |
| 벡터 DB             | FAISS IndexFlatIP                                                        |
| 이상 탐지           | IsolationForest + 1D-CNN AutoEncoder                                     |
| 데이터셋            | [MetroPT-3](https://archive.ics.uci.edu/dataset/791) — Metro APU 압축기 |
| API                 | FastAPI + Uvicorn                                                        |
| UI                  | Streamlit + Plotly                                                       |
| 배포                | Docker Compose (GPU 패스스루)                                            |

---

## 파일 구성

```
llm_agent_phm/
├── data/
│   ├── metropt3/                       # MetroPT-3 CSV (별도 다운로드)
│   └── docs/                           # SOP/매뉴얼 마크다운 (5종)
├── notebooks/                          # 학습/테스트 노트북
│   ├── 01_data_exploration.ipynb       # EDA + 가상 데이터 준비
│   ├── 02_anomaly_detection.ipynb      # IF + ConvAE 학습/평가
│   ├── 03_rag_setup.ipynb              # FAISS 인덱싱
│   ├── 04_tools_demo.ipynb             # 5개 tool 단위 테스트
│   └── 05_langgraph_agent.ipynb        # 에이전트 테스트
├── src/
│   ├── data/loader.py                  # MetroPT-3 로더, SensorDB, FAILURE_WINDOWS
│   ├── data/synthetic_history.py       # 가상 고장 이력 (라벨 시간대 정합)
│   ├── models/anomaly.py               # IFAnomalyModel + AEAnomalyModel
│   ├── models/llm.py                   # Qwen2.5 INT4 로더
│   ├── rag/indexer.py                  # 마크다운 청크 + FAISS 인덱싱
│   ├── rag/retriever.py                # 하이브리드(semantic + keyword) 검색
│   ├── agent/
│   │   ├── tools.py                    # 5개 LangChain @tool
│   │   ├── state.py                    # AgentState (TypedDict)
│   │   ├── nodes.py                    # 노드 함수 (supervisor 등)
│   │   └── graph.py                    # StateGraph 컴파일
│   └── api/
│       ├── main.py                     # FastAPI 앱 (lifespan 모델 로드)
│       └── schemas.py                  # Pydantic 요청/응답 모델
├── ui/
│   └── streamlit_app.py                # 채팅 + 시계열 차트 + trace UI
├── tests/
│   ├── conftest.py                     # Fake fixture (LLM/데이터 없이 테스트)
│   ├── test_tools.py
│   └── test_agent.py
├── models_artifacts/                   # 학습된 모델 + RAG 인덱스
├── Dockerfile.api                      # PyTorch 2.5 + CUDA 12.4 베이스
├── Dockerfile.ui                       # Slim Python + Streamlit
├── docker-compose.yml                  # api + ui 동시 기동
└── requirements.txt
```

---

## 빠른 시작

### Makefile

대부분의 작업은 [Makefile](./Makefile)의 단축 명령으로 실행할 수 있습니다.

```bash
make help              # 사용 가능한 모든 타겟 보기
make install           # 의존성 설치
make api               # FastAPI 서버 기동
make ui                # Streamlit UI 기동 (별도 터미널)
make test              # pytest 실행
make up                # Docker Compose로 api + ui 동시 기동
```

> WSL2 환경에서 테스트

### 수동 실행 (Makefile 미사용 시)

### 1. 환경 준비

```powershell
pip install -r requirements.txt
```

### 2. MetroPT-3 데이터 다운로드

[UCI 공식 페이지](https://archive.ics.uci.edu/dataset/791)에서 CSV를 받아 `data/metropt3/` 안에 배치합니다 (약 200MB).

### 3. 노트북 실행

```
01_data_exploration.ipynb     # EDA + 가상 이력 CSV 생성
02_anomaly_detection.ipynb    # IF/ConvAE 학습 -> models_artifacts/*
03_rag_setup.ipynb            # 매뉴얼/이력 FAISS 인덱싱
04_tools_demo.ipynb           # 5개 tool 단위 테스트
05_langgraph_agent.ipynb      # Qwen2.5-7B 로드 후 에이전트 테스트
```

---

## 5개 Tool 명세


| Tool              | 입력                                             | 출력                                                  |
| ------------------- | -------------------------------------------------- | ------------------------------------------------------- |
| `query_sensor`    | equipment_id, start, end, sensors                | 통계 요약 JSON (mean/min/max/std + fault_label_ratio) |
| `detect_anomaly`  | equipment_id, start, end                         | 이상 점수 + verdict + 의심 센서 top3                  |
| `search_manual`   | query, k                                         | 매뉴얼/SOP 청크 top-k                                 |
| `search_history`  | query, equipment_id, k                           | 과거 사례 top-k                                       |
| `draft_workorder` | equipment_id, diagnosis, actions, priority, refs | 작업지시서 Markdown                                   |

각 tool은 LangChain `@tool` 데코레이터로 정의되어 있습니다.

---

## 테스트 시나리오

### 시나리오 1 — 단순 상태 점검

```
"1호 압축기 2월 15일 상태 점검해줘"
-> supervisor: intent=status_check
-> sensor + anomaly 병렬 호출
-> synthesizer가 "정상 운전 중" 보고
```

### 시나리오 2 — 이상 진단

```
"3호 압축기 압력이 이상한데 매뉴얼이랑 과거 사례 보고 진단해줘"
-> supervisor: intent=diagnosis
-> sensor + anomaly + manual + history 모두 병렬 호출
-> synthesizer: "Air Leak 의심 (DV O-ring 노후 가능성). 과거 INC-2020-0607 사례 참조"
```

### 시나리오 3 — 작업지시서 자동 생성

```
"공기 누설 의심된다, 작업지시서 초안 만들어줘"
-> supervisor: intent=workorder
-> 풀 파이프라인 + workorder 노드까지
-> Markdown 작업지시서 출력 (담당자 검토용 초안)
```

각 시나리오 응답 시간은 RTX 4060 + Qwen2.5-7B INT4 기준 약 15~35초입니다.

---

## 배포 (FastAPI + Streamlit)

주피터 노트북 내용을 실제 서비스 형태로 패키징한 단계입니다.

### API 엔드포인트


| Method | Path             | 용도                                         |
| -------- | ------------------ | ---------------------------------------------- |
| GET    | `/health`        | 모델/RAG/에이전트 로드 상태                  |
| GET    | `/equipment`     | 등록된 가상 설비 목록                        |
| POST   | `/sensors/{eid}` | 시계열 raw 데이터 (UI 차트용)                |
| POST   | `/agent/query`   | 에이전트 질의 (`stream=true`로 SSE 스트리밍) |

Swagger UI는 `http://localhost:8000/docs` 에서 확인할 수 있습니다.

### 로컬 실행

**1) API 서버**

```powershell
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
# 첫 기동 시 모델 로드에 약 1~3분 소요됩니다 (Qwen2.5 미캐시 시 더 오래)
```

**2) Streamlit UI** (별도 터미널)

```powershell
$env:API_URL = "http://localhost:8000"
streamlit run ui/streamlit_app.py
# 브라우저: http://localhost:8501
```

UI는 다음과 같이 구성됩니다.

- 좌측: 설비 선택 + 시간 범위 + Plotly 시계열 차트 + 테스트 프리셋 (정상 / Air Leak)
- 우측: 채팅 인터페이스 + 호출된 노드 trace + 작업지시서 Markdown 다운로드

### Docker Compose 실행

```bash
# WSL/Linux 환경
sudo docker compose build
sudo docker compose up -d
sudo docker compose logs -f api
```

NVIDIA Container Toolkit이 WSL2에 설치되어 있어야 GPU 추론이 활성화됩니다.

### 테스트

```powershell
pip install pytest
pytest tests/ -v
```

---

## 기존 `llm_phm/` 대비 개선점


| 측면     | llm_phm (기존)             | llm_agent_phm (본 프로젝트)                    |
| ---------- | ---------------------------- | ------------------------------------------------ |
| 흐름     | 1턴 (질문 -> 검색 -> 답변) | 멀티스텝 (라우팅 -> 다중 도구 -> 종합 -> 분기) |
| 데이터   | 단일 (베어링 신호)         | 다중 (시계열 + 이상탐지 + 문서 + 이력)         |
| LLM 역할 | 답변 생성                  | intent 분류 + 종합 진단 + 구조화 출력          |
| 의사결정 | 고정 파이프라인            | 사용자 의도에 따라 동적 분기                   |
| 출력     | 텍스트                     | 진단 보고서 + 작업지시서 Markdown              |
| 가시성   | 없음                       | 노드별 trace 로그                              |
| 배포     | 노트북 only                | FastAPI + Streamlit + Docker Compose           |
| 테스트   | 없음                       | pytest (LLM 없이 동작)                         |

---

## 주요 학습 포인트

이 프로젝트를 진행하며 다음 항목들을 실증적으로 확인하였습니다.

### 1. AutoEncoder의 distribution shift 문제와 해결

초기 ConvAE는 train(2\~5월)과 test(5\~9월) 시기의 운전 조건 변화로 PR-AUC 0.07까지 떨어졌습니다. **Per-window z-score 정규화** (각 윈도우의 자체 mean/std로 정규화)를 적용한 결과, PR-AUC가 0.91로 개선되었습니다. 모델 아키텍처보다 데이터 자체의 표현이 결정적이라는 사실을 확인할 수 있었습니다.

### 2. 시계열 데이터의 timestamp 기반 분할

인덱스 비율(7:3) 분할은 데이터 갭(누락 시간대) 때문에 캘린더 경계와 어긋납니다. 본 데이터에는 약 30일치 갭이 있어 60% 인덱스가 캘린더상 6월 중순으로 밀렸습니다. **Timestamp 기반 분할**(2020-05-25 기준)로 변경하여 train/test의 fault 분포 일관성을 확보했습니다.

### 3. LLM 기반 라우팅의 한계와 결정론적 정책 보강

Supervisor LLM에게 `intent` + `needs_*` 모두 결정하게 했더니 보수적 응답이 발생해 도구 호출이 누락되는 사례가 있었습니다. **Intent별 needs를 코드로 강제**하는 정책을 추가하여 재현성과 신뢰성을 확보했습니다.

### 4. 데이터 정합성 설계

실제 라벨 구간(MetroPT-3 Description)과 가상 CMMS 이력의 시간/설비를 SensorDB의 가상 설비 오프셋(APU-01: +0d, APU-02: +30d, APU-03: +60d)에 맞춰 정렬했습니다. 그 결과, 에이전트가 "APU-03 6월 11일 진단" 요청 시 RAG가 끌어오는 과거 사례(INC-2020-0607)가 자연스럽게 같은 사건의 전조를 가리킵니다.

---

## 참고 사항

- 이 프로젝트는 학습 및 포트폴리오 목적으로 작성되었습니다.
- MetroPT-3 데이터셋은 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 라이선스를 따릅니다.
- Qwen2.5-7B-Instruct 모델은 [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) 라이선스를 따릅니다.
- 가상 매뉴얼/이력은 도메인 학습용으로 작성한 합성 데이터이며, 실제 운영에 사용해서는 안 됩니다.
