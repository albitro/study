# CWRU PHM Inference API - Makefile

# 변수 
COMPOSE      ?= docker compose
SERVICE      ?= api
DATA_DIR     ?= ./data/raw
MODEL_PATH   ?= ./models/rf_v1.joblib
RPM          ?= 1772
PORT         ?= 8000
TEST_FILE    ?= /app/data/raw/OR007_6_1_136.mat
N_SEGMENTS   ?= 5

RUN_IN_CONTAINER = $(COMPOSE) run --rm --no-deps $(SERVICE)

.DEFAULT_GOAL := help

# 메타 
.PHONY: help
help: ## 사용 가능한 명령어 목록 출력
	@echo ""
	@echo "  CWRU PHM Inference API"
	@echo "  ───────────────────────────────────────────────"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""


# 데이터 / 모델 가드
.PHONY: check-data
check-data: ## CWRU .mat 파일이 data/raw/에 있는지 확인 (호스트에서)
	@echo "Checking data files in $(DATA_DIR) ..."
	@missing=0; \
	for f in Time_Normal_1_098.mat IR007_1_110.mat IR014_1_175.mat IR021_1_214.mat \
	         OR007_6_1_136.mat OR014_6_1_202.mat OR021_6_1_239.mat \
	         B007_1_123.mat B014_1_190.mat B021_1_227.mat; do \
		if [ -f "$(DATA_DIR)/$$f" ]; then \
			echo "  [OK]      $$f"; \
		else \
			echo "  [MISSING] $$f"; \
			missing=$$((missing+1)); \
		fi; \
	done; \
	if [ $$missing -gt 0 ]; then \
		echo ""; \
		echo "  $$missing file(s) missing. CWRU Bearing Data Center에서 받아 $(DATA_DIR)/에 넣어주세요."; \
		echo "  https://engineering.case.edu/bearingdatacenter"; \
		exit 1; \
	fi

.PHONY: check-model
check-model: ## 모델 파일이 있는지 확인 (호스트에서)
	@if [ ! -f "$(MODEL_PATH)" ]; then \
		echo "  Model not found: $(MODEL_PATH)"; \
		echo "  먼저 'make train'을 실행하여 모델을 만들어주세요."; \
		exit 1; \
	else \
		echo "  Model OK: $(MODEL_PATH)"; \
	fi

# Docker 이미지 
.PHONY: build
build: ## Docker 이미지 빌드 (requirements.txt 변경 시 재실행)
	$(COMPOSE) build

# 학습 (컨테이너 안에서 실행)
.PHONY: train
train: check-data build ## 컨테이너 안에서 모델 학습 (data/raw/에 .mat 파일 필요)
	$(RUN_IN_CONTAINER) python scripts/train.py \
		--data-dir /app/data/raw \
		--output /app/models/rf_v1.joblib \
		--rpm $(RPM)

# 서버
.PHONY: up
up: check-model build ## Docker 서버 시작 (백그라운드)
	$(COMPOSE) up -d
	@echo ""
	@echo "  Server started. Try: make health"
	@echo "  Swagger UI: http://localhost:$(PORT)/docs"

.PHONY: up-fg
up-fg: check-model build ## Docker 서버 시작 (포그라운드, 로그 함께 보기)
	$(COMPOSE) up

.PHONY: down
down: ## Docker 서버 종료
	$(COMPOSE) down

.PHONY: restart
restart: ## Docker 서버 재시작
	$(COMPOSE) restart

.PHONY: logs
logs: ## Docker 로그 보기 (Ctrl+C로 종료)
	$(COMPOSE) logs -f

.PHONY: ps
ps: ## 컨테이너 상태 확인
	$(COMPOSE) ps

.PHONY: shell
shell: ## 실행 중인 api 컨테이너에 셸로 접속 (디버깅용)
	$(COMPOSE) exec $(SERVICE) /bin/bash

# 테스트 / 검증
.PHONY: health
health: ## 서버 헬스체크 (호스트에서 curl)
	@curl -fsS http://localhost:$(PORT)/health || echo "  Server not reachable"
	@echo ""

.PHONY: info
info: ## 서버에 로드된 모델 정보 조회
	@curl -fsS http://localhost:$(PORT)/model/info | python3 -m json.tool 2>/dev/null \
		|| curl -fsS http://localhost:$(PORT)/model/info \
		|| echo "  Server not reachable"

.PHONY: examples
examples: ## 합성 예제 4종 생성 (examples/normal.json, inner.json, outer.json, ball.json)
	@$(COMPOSE) run --rm --no-deps $(SERVICE) sh -c "\
		python scripts/make_example_payload.py synthetic normal --output /app/examples/normal.json && \
		python scripts/make_example_payload.py synthetic inner  --output /app/examples/inner.json && \
		python scripts/make_example_payload.py synthetic outer  --output /app/examples/outer.json && \
		python scripts/make_example_payload.py synthetic ball   --output /app/examples/ball.json"

.PHONY: example-curl
example-curl: ## 외륜 결함 예제를 curl로 /predict에 보내기
	@if [ ! -f examples/outer.json ]; then \
		echo "  examples/outer.json not found. Run 'make examples' first."; exit 1; \
	fi
	@echo "POST /predict with examples/outer.json"
	@curl -fsS -X POST http://localhost:$(PORT)/predict \
		-H "Content-Type: application/json" \
		-d @examples/outer.json \
		| python3 -m json.tool

.PHONY: example-curl-all
example-curl-all: ## 4종 예제(normal/inner/outer/ball)를 모두 curl로 보내고 핵심 결과만 출력
	@for kind in normal inner outer ball; do \
		if [ ! -f examples/$$kind.json ]; then \
			echo "  examples/$$kind.json not found. Run 'make examples' first."; exit 1; \
		fi; \
		printf "  %-7s -> " $$kind; \
		curl -fsS -X POST http://localhost:$(PORT)/predict \
			-H "Content-Type: application/json" \
			-d @examples/$$kind.json \
			| python3 -c "import json,sys; d=json.load(sys.stdin); p=d['prediction']; dg=d['diagnosis']; print(f\"{p['label']:7s} ({p['probabilities'][p['label']]:.0%}) | peak={dg['dominant_peak_hz']:.1f}Hz ({dg['nearest_fault']}) | SNR={dg['snr']:.1f}x\")" \
			|| echo "  request failed"; \
	done

.PHONY: test-client
test-client: ## 실행 중인 api 컨테이너 안에서 테스트 클라이언트 실행 (먼저 make up 필요)
	@$(COMPOSE) ps --services --filter "status=running" | grep -q "^$(SERVICE)$$" \
		|| (echo "  Server is not running. Run 'make up' first." && exit 1)
	$(COMPOSE) exec $(SERVICE) python scripts/test_client.py $(TEST_FILE) \
		--url http://localhost:8000 \
		--n $(N_SEGMENTS) \
		--rpm $(RPM)

# 정리
.PHONY: clean
clean: ## 파이썬 캐시 정리 (호스트의 __pycache__)
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache 2>/dev/null || true

.PHONY: clean-model
clean-model: ## 학습된 모델 삭제 (재학습 필요)
	rm -f $(MODEL_PATH) $(MODEL_PATH:.joblib=.meta.json)

.PHONY: clean-all
clean-all: clean clean-model down ## 캐시 + 모델 + 컨테이너 모두 정리
	$(COMPOSE) down --rmi local --volumes 2>/dev/null || true
