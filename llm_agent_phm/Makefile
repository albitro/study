# Industrial Equipment LLM Agent - Makefile

# 변수
COMPOSE         ?= docker compose
SERVICE         ?= api
DATA_DIR        ?= ./data/metropt3
ARTIFACTS_DIR   ?= ./models_artifacts
DOCS_DIR        ?= ./data/docs
LLM_MODEL_ID    ?= Qwen/Qwen2.5-7B-Instruct
LLM_QUANT       ?= int4
HF_CACHE_DIR    ?= $(HOME)/.cache/huggingface
API_PORT        ?= 8000
UI_PORT         ?= 8501

RUN_IN_CONTAINER = $(COMPOSE) run --rm --no-deps $(SERVICE)

.DEFAULT_GOAL := help

# 메타
.PHONY: help
help: ## 사용 가능한 명령어 목록 출력
	@echo ""
	@echo "  Industrial Equipment LLM Agent"
	@echo "  ───────────────────────────────────────────────"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / { printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

# 데이터 / 모델 가드
.PHONY: check-data
check-data: ## MetroPT-3 CSV가 data/metropt3/에 있는지 확인
	@echo "Checking MetroPT-3 CSV in $(DATA_DIR) ..."
	@if [ -z "$$(ls $(DATA_DIR)/*.csv 2>/dev/null)" ]; then \
		echo "  [MISSING] *.csv"; \
		echo ""; \
		echo "  MetroPT-3 데이터셋을 다운로드하여 $(DATA_DIR)/ 안에 넣어주세요."; \
		echo "  https://archive.ics.uci.edu/dataset/791"; \
		exit 1; \
	else \
		for f in $(DATA_DIR)/*.csv; do echo "  [OK] $$f"; done; \
	fi

.PHONY: check-artifacts
check-artifacts: ## 학습된 모델 + RAG 인덱스가 models_artifacts/에 있는지 확인
	@echo "Checking artifacts in $(ARTIFACTS_DIR) ..."
	@missing=0; \
	for f in convae_v1.pt iforest_v1.joblib anomaly_meta.json rag/manual/index.faiss rag/history/index.faiss; do \
		if [ -f "$(ARTIFACTS_DIR)/$$f" ]; then \
			echo "  [OK]      $$f"; \
		else \
			echo "  [MISSING] $$f"; \
			missing=$$((missing+1)); \
		fi; \
	done; \
	if [ $$missing -gt 0 ]; then \
		echo ""; \
		echo "  $$missing 파일이 없습니다. 노트북을 순서대로 실행해 모델/인덱스를 생성하세요:"; \
		echo "    notebooks/02_anomaly_detection.ipynb  (이상탐지 모델)"; \
		echo "    notebooks/03_rag_setup.ipynb          (FAISS 인덱스)"; \
		exit 1; \
	fi

# 환경 / 노트북
.PHONY: install
install: ## 의존성 설치 (pip install -r requirements.txt)
	pip install -r requirements.txt

.PHONY: notebooks
notebooks: ## Jupyter Lab 기동 (notebooks/ 디렉토리)
	jupyter lab --notebook-dir=notebooks

# 로컬 직접 실행 (Docker 미사용)
.PHONY: api
api: check-artifacts ## 호스트에서 FastAPI 기동 (uvicorn --reload)
	python -m uvicorn src.api.main:app --host 0.0.0.0 --port $(API_PORT) --reload

.PHONY: ui
ui: ## 호스트에서 Streamlit UI 기동 (별도 터미널 권장)
	streamlit run ui/streamlit_app.py --server.port $(UI_PORT)

.PHONY: test
test: ## pytest 실행 (LLM/실제 데이터 불필요, Fake fixture 사용)
	python -m pytest tests/ -v

# Docker 이미지
.PHONY: build
build: ## Docker 이미지 빌드 (api + ui)
	$(COMPOSE) build

# Docker 서버
.PHONY: up
up: check-data check-artifacts ## Docker 서버 시작 (백그라운드)
	HF_CACHE_DIR=$(HF_CACHE_DIR) LLM_MODEL_ID=$(LLM_MODEL_ID) LLM_QUANT=$(LLM_QUANT) \
	  $(COMPOSE) up -d
	@echo ""
	@echo "  Server starting. 첫 기동 시 모델 로드 1~3분 소요."
	@echo "  API:        http://localhost:$(API_PORT)/docs"
	@echo "  UI:         http://localhost:$(UI_PORT)"
	@echo "  Logs:       make logs"
	@echo "  Health:     make health"

.PHONY: up-fg
up-fg: check-data check-artifacts ## Docker 서버 시작 (포그라운드, 로그 함께 보기)
	HF_CACHE_DIR=$(HF_CACHE_DIR) LLM_MODEL_ID=$(LLM_MODEL_ID) LLM_QUANT=$(LLM_QUANT) \
	  $(COMPOSE) up

.PHONY: down
down: ## Docker 서버 종료
	$(COMPOSE) down

.PHONY: restart
restart: ## api 컨테이너 재시작 (코드 변경 반영, 모델 재로드 1~3분)
	$(COMPOSE) restart $(SERVICE)
	@echo ""
	@echo "  Restarted. 모델 재로드까지 1~3분 대기 필요."

.PHONY: logs
logs: ## api 로그 실시간 보기 (Ctrl+C로 종료)
	$(COMPOSE) logs -f $(SERVICE)

.PHONY: logs-ui
logs-ui: ## ui 로그 실시간 보기
	$(COMPOSE) logs -f ui

.PHONY: ps
ps: ## 컨테이너 상태 확인
	$(COMPOSE) ps

.PHONY: shell
shell: ## 실행 중인 api 컨테이너에 셸로 접속 (디버깅용)
	$(COMPOSE) exec $(SERVICE) /bin/bash

# 테스트 / 검증
.PHONY: health
health: ## 서버 헬스체크 (호스트에서 curl)
	@curl -fsS http://localhost:$(API_PORT)/health | python3 -m json.tool 2>/dev/null \
		|| curl -fsS http://localhost:$(API_PORT)/health \
		|| echo "  Server not reachable"
	@echo ""

.PHONY: equipment
equipment: ## 등록된 가상 설비 목록 조회
	@curl -fsS http://localhost:$(API_PORT)/equipment | python3 -m json.tool 2>/dev/null \
		|| echo "  Server not reachable"

.PHONY: example-status
example-status: ## 시나리오 1: APU-01 정상 구간 상태 점검 (status_check)
	@echo "POST /agent/query | intent=status_check"
	@curl -fsS -X POST http://localhost:$(API_PORT)/agent/query \
		-H "Content-Type: application/json" \
		-d '{"query": "1호 압축기 상태 점검해줘", "equipment_id": "APU-01", "time_range": ["2020-02-15T00:00:00", "2020-02-17T00:00:00"]}' \
		| python3 -c "import json,sys; d=json.load(sys.stdin); print(f\"  intent      : {d['intent']}\"); print(f\"  equipment   : {d['equipment_id']}\"); print(f\"  trace nodes : {[t['node'] for t in d['trace']]}\"); print(f\"\\n--- diagnosis ---\\n{d['diagnosis']}\")"

.PHONY: example-diagnosis
example-diagnosis: ## 시나리오 2: APU-03 Air Leak 진단 (diagnosis)
	@echo "POST /agent/query | intent=diagnosis"
	@curl -fsS -X POST http://localhost:$(API_PORT)/agent/query \
		-H "Content-Type: application/json" \
		-d '{"query": "압력이 이상한데 매뉴얼이랑 과거 사례 보고 진단해줘", "equipment_id": "APU-03", "time_range": ["2020-06-11T00:00:00", "2020-06-13T00:00:00"]}' \
		| python3 -c "import json,sys; d=json.load(sys.stdin); print(f\"  intent      : {d['intent']}\"); print(f\"  trace nodes : {[t['node'] for t in d['trace']]}\"); print(f\"\\n--- diagnosis ---\\n{d['diagnosis']}\")"

.PHONY: example-workorder
example-workorder: ## 시나리오 3: 작업지시서 자동 생성 (workorder)
	@echo "POST /agent/query | intent=workorder"
	@curl -fsS -X POST http://localhost:$(API_PORT)/agent/query \
		-H "Content-Type: application/json" \
		-d '{"query": "공기 누설 의심된다, 작업지시서 초안 만들어줘", "equipment_id": "APU-03", "time_range": ["2020-06-11T00:00:00", "2020-06-13T00:00:00"]}' \
		| python3 -c "import json,sys; d=json.load(sys.stdin); print(f\"  intent      : {d['intent']}\"); print(f\"  trace nodes : {[t['node'] for t in d['trace']]}\"); print(f\"\\n--- workorder ---\\n{d['workorder']}\")"

.PHONY: example-all
example-all: example-status example-diagnosis example-workorder ## 3개 시나리오를 모두 호출

# 정리
.PHONY: clean
clean: ## 파이썬 캐시 정리 (__pycache__, .pytest_cache 등)
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache 2>/dev/null || true

.PHONY: clean-artifacts
clean-artifacts: ## 학습된 모델/RAG 인덱스 삭제 (재학습 필요)
	rm -rf $(ARTIFACTS_DIR)/convae_v1.pt $(ARTIFACTS_DIR)/iforest_v1.joblib \
	       $(ARTIFACTS_DIR)/anomaly_meta.json $(ARTIFACTS_DIR)/rag/

.PHONY: clean-all
clean-all: clean clean-artifacts down ## 캐시 + 모델 + 컨테이너 모두 정리
	$(COMPOSE) down --rmi local --volumes 2>/dev/null || true
