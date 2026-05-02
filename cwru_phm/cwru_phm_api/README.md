# CWRU PHM Inference API

CWRU 베어링 진동 신호를 받아 베어링 상태를 분류하는 FastAPI 입니다.

CWRU 베어링 데이터 기반 PHM 신호처리 프로젝트([albitro/study/cwru_phm](https://github.com/albitro/study/tree/main/cwru_phm))의 분류 파이프라인을 운영 환경으로 옮긴 것입니다. 4096 샘플(약 0.34초) 단위로 진단합니다.

## 입출력

**입력**: 4096 샘플 진동 신호 + 샘플링 주파수 + RPM

**출력**: 분류 결과(Normal/Inner/Outer/Ball) + 14개 특징 + 진단 근거(포락선 dominant peak, SNR, 매칭된 결함 주파수)

## 테스트 환경

```
linux, docker, docker compose, make, curl
```

## 빠른 시작

```bash
# 0. 사용 가능한 명령어 보기
make help                    # 또는 그냥 make

# 1. Docker 이미지 빌드 (최초 1회)
make build

# 2. 데이터 준비 (CWRU에서 직접 다운로드 후 ./data/raw/에 배치)
#    https://engineering.case.edu/bearingdatacenter
make check-data              # 필요한 파일이 모두 있는지 검증

# 3. 모델 학습 (컨테이너 안에서 실행됨)
make train                   # -> models/rf_v1.joblib 생성

# 4. 서버 시작
make up                      # 백그라운드
# 또는
make up-fg                   # 포그라운드 (로그 함께 보기)

# 5. 동작 확인
make health                  # GET /health (호스트에서 curl)
make info                    # GET /model/info
make examples                # 합성 예제 페이로드 4종 생성
make example-curl-all        # 4개 페이로드를 curl로 모두 호출 (한 줄 요약)
make example-curl            # outer 페이로드 하나로 응답 전체 보기
make test-client             # 컨테이너 안에서 테스트 클라이언트 실행 (CWRU 데이터 필요)

# 6. 종료
make down
```

`http://localhost:8000/docs`에서 Swagger UI를 확인할 수 있습니다.

## 주요 Make 타겟


| 타겟                    | 용도                                             |
| ------------------------- | -------------------------------------------------- |
| `make help`             | 모든 명령어 목록                                 |
| `make build`            | Docker 이미지 빌드                               |
| `make check-data`       | CWRU .mat 파일 존재 검증                         |
| `make train`            | 컨테이너 안에서 모델 학습                        |
| `make up`               | 서버 시작 (백그라운드)                           |
| `make up-fg`            | 서버 시작 (포그라운드)                           |
| `make down`             | 서버 종료                                        |
| `make restart`          | 서버 재시작                                      |
| `make logs`             | Docker 로그 보기                                 |
| `make ps`               | 컨테이너 상태                                    |
| `make shell`            | 컨테이너 안 셸 접속 (디버깅용)                   |
| `make health`           | 서버 헬스체크 (curl)                             |
| `make info`             | 로드된 모델 메타정보                             |
| `make examples`         | 합성 예제 데이터 4종 생성                        |
| `make example-curl`     | curl로 outer 합성 데이터 호출하고 응답 전체 출력 |
| `make example-curl-all` | curl로 4종 모두 호출하고 핵심 결과만 한 줄씩     |
| `make test-client`      | CWRU .mat 파일로 테스트 클라이언트 호출          |
| `make clean`            | Python 캐시 정리                                 |
| `make clean-model`      | 학습된 모델 삭제                                 |
| `make clean-all`        | 캐시 + 모델 + 컨테이너 모두 정리                 |

```bash
make train RPM=1797
make test-client TEST_FILE=/app/data/raw/IR007_1_110.mat N_SEGMENTS=10
```

`TEST_FILE`은 컨테이너 안 경로로 지정해야 합니다(`/app/data/raw/...`). 호스트의 `./data/raw/`가 컨테이너의 `/app/data/raw/`로 마운트됩니다.

## API 엔드포인트


| 메서드 | 경로          | 용도                                       |
| -------- | --------------- | -------------------------------------------- |
| GET    | `/health`     | 헬스체크, 모델 로드 상태                   |
| GET    | `/model/info` | 모델 버전, 학습 정확도, feature/class 이름 |
| POST   | `/predict`    | 4096 샘플 1세그먼트 분류                   |

`/predict` 응답은 다음 5개 블록으로 구성됩니다:

- `prediction`: 라벨 + 클래스별 확률
- `features`: 14개 특징 (시간/주파수/포락선)
- `diagnosis`: 포락선 dominant peak + SNR + 매칭된 결함 주파수
- `fault_frequencies`: 입력 RPM에서 계산된 이론적 결함 주파수
- `meta`: 모델 버전, 추론 시간

## /predict 호출 예시

### Make로 한 번에

```bash
make examples                # examples/normal.json, inner.json, outer.json, ball.json 생성
make example-curl-all        # 4개를 모두 curl로 호출하고 한 줄씩 결과 출력
```

출력:

```
  normal  -> Normal  (100%) | peak=436.5Hz (None) | SNR=2.5x
  inner   -> Inner   (100%) | peak=161.1Hz (BPFI) | SNR=29.9x
  outer   -> Outer   (100%) | peak=105.5Hz (BPFO) | SNR=34.4x
  ball    -> Ball    (65%)  | peak=140.6Hz (2*BSF) | SNR=30.9x
```

### curl로 직접

```bash
curl -X POST http://localhost:8000/predict \
    -H "Content-Type: application/json" \
    -d @examples/outer.json
```

### 응답 예시 (outer.json)

```json
{
  "prediction": {
    "label": "Outer",
    "class_id": 2,
    "probabilities": {"Normal": 0.0, "Inner": 0.0, "Outer": 1.0, "Ball": 0.0}
  },
  "features": {
    "time_domain": {
      "RMS": 0.7236, "Kurtosis": 3.92, "Crest": 2.91,
      "P2P": 4.11, "Skewness": 0.06, "Std": 0.72
    },
    "freq_domain": {
      "FFT_0_200": 0.0007, "FFT_200_500": 0.0008, "FFT_2k_5k": 1.033
    },
    "envelope": {
      "Env_BPFO": 0.247, "Env_BPFI": 0.0002, "Env_BSF": 0.0002,
      "Env_0_200": 0.266, "Env_200_500": 0.116
    }
  },
  "diagnosis": {
    "dominant_peak_hz": 105.47,
    "dominant_peak_amp": 0.465,
    "snr": 34.36,
    "nearest_fault": "BPFO",
    "nearest_fault_freq_hz": 105.88,
    "delta_hz": -0.41
  },
  "fault_frequencies": {
    "rpm": 1772.0, "fr": 29.53,
    "BPFO": 105.88, "BPFI": 159.92,
    "BSF": 69.62, "two_BSF": 139.24, "FTF": 11.76
  },
  "meta": {
    "model_version": "rf_v1",
    "inference_ms": 14.48,
    "segment_length": 4096,
    "fs": 12000, "rpm": 1772.0
  }
}
```

응답 해석: 분류는 **Outer fault (확률 100%)**, 진단 근거는 **포락선 dominant peak가 105.47Hz로 BPFO 이론값(105.88Hz)과 0.41Hz 차이**, **SNR 34배**로 매우 명확합니다.

### Python으로 호출

```python
import json, httpx
with open("examples/outer.json") as f:
    payload = json.load(f)
r = httpx.post("http://localhost:8000/predict", json=payload, timeout=10)
print(r.json()["prediction"]["label"])
```

## 폴더 구조

```
cwru_phm_api/
├── Makefile                      # 명령어 작성 (모두 Docker 기반)
├── api/                          # FastAPI 애플리케이션
│   ├── main.py                   # 앱 + lifespan
│   ├── config.py                 # 환경 변수
│   ├── core/   
│   │   ├── fault_freq.py         # BPFO/BPFI/BSF 계산
│   │   ├── features.py           # 14개 특징 추출
│   │   ├── diagnosis.py          # 포락선 진단
│   │   └── model.py              # 모델 로드 + 추론 래퍼
│   ├── routers/                  # 엔드포인트
│   │   ├── health.py
│   │   └── predict.py
│   └── schemas/                  # Pydantic 모델
│       ├── common.py
│       └── predict.py
├── scripts/
│   ├── make_example_payload.py   # 합성 예제 샘플 생성
│   ├── train.py                  # 모델 학습 (컨테이너에서 실행)
│   └── test_client.py            # 테스트 클라이언트 (컨테이너에서 실행)
├── models/                       # 학습된 모델 (호스트, 컨테이너 간 볼륨 마운트)
├── data/raw/                     # CWRU .mat (read-only 마운트) / 데이터는 포함되지 않습니다
├── docker/Dockerfile
├── docker-compose.yml
└── requirements.txt              # Docker 이미지 빌드 시 사용
```

## 참고

- **세그먼트 길이는 4096 고정**
- **확률값 해석 주의**: RF의 `predict_proba`는 트리 투표 비율이라, 0.95가 "신뢰도 95%"를 의미하지는 않습니다.
- **CWRU 도메인 한계**: CWRU 베어링 데이터 기반 PHM 신호처리 프로젝트의 결과가 그대로 반영됩니다. 학습 데이터가 단일 베어링(SKF 6205), 단일 RPM, 인공 결함이기 때문에 다른 환경에 그대로 사용할 수 없습니다. 운영 시 재학습 필요.
