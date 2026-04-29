# 01. Google Cloud 데이터 분석 & BigQuery

> 출처: [Google Skills Boost - Introduction to Data Analytics on Google Cloud](https://www.skills.google/paths/18/course_templates/578)

---

## 📚 목차

1. [과정 소개](#1-과정-소개)
2. [Google Cloud 데이터 분석 수명 주기](#2-google-cloud-데이터-분석-수명-주기)
3. [Google Cloud 데이터 소스 및 저장 방법](#3-google-cloud-데이터-소스-및-저장-방법)
4. [BigQuery 소개](#4-bigquery-소개)
5. [BigQuery 작동 방식](#5-bigquery-작동-방식)
6. [BigQuery의 데이터 구성 방식](#6-bigquery의-데이터-구성-방식)
7. [핵심 정리](#7-핵심-정리)

---

## 1. 과정 소개

### 1.1. 학습 대상

- 데이터 분석가
- BigQuery와 Looker로 인사이트를 얻고자 하는 학습자

### 1.2. 학습 목표

- 데이터 분석 워크플로 및 다양한 분석 유형 이해
- Google Cloud 데이터 분석 제품 파악
- Google Cloud의 데이터 소스, 데이터 구조, 데이터 스토리지 옵션 이해
- BigQuery, Looker, Looker Studio를 활용한 데이터 분석 및 시각화

---

## 2. Google Cloud 데이터 분석 수명 주기

### 2.1. 데이터 분석 수명 주기란?

- 데이터를 **수집 → 저장 → 처리 → 분석**하여 인사이트를 추출하는 과정
- 데이터 기반 의사결정의 핵심
- **반복 프로세스**: 여러 단계를 자주 오가게 됨

### 2.2. 단계별 Google Cloud 제품


| 단계          | 주요 제품                                                                       | 설명                             |
| --------------- | --------------------------------------------------------------------------------- | ---------------------------------- |
| 수집(Ingest)  | Pub/Sub, Dataflow, Dataproc, Cloud Data Fusion                                  | 실시간 및 일괄 데이터 수집, 처리 |
| 저장(Store)   | Cloud Storage, Cloud SQL, Cloud Spanner, Bigtable, Firestore, AlloyDB, BigQuery | 데이터 특성에 따른 다양한 저장소 |
| 처리(Process) | Dataproc(일괄), Dataflow(스트리밍), Cloud Data Fusion(통합)                     | 데이터 변환 및 가공              |
| 분석(Analyze) | BigQuery, Looker, Looker Studio                                                 | SQL 기반 분석 및 시각화          |
| ML 활용       | Vertex AI, AutoML, Vertex AI Workbench, TensorFlow                              | 머신러닝 기반 인사이트 도출      |

### 2.3. 주요 도구 정리

- **Pub/Sub**: 수집/메시징 (스트리밍)
- **Dataflow**: 분석/처리 (스트리밍)
- **Cloud Data Fusion**: 코드 작성 불필요한 ETL 도구 (온프레미스 + 클라우드 통합)
- **Dataproc**: 일괄 처리(Batch)

---

## 3. Google Cloud 데이터 소스 및 저장 방법

### 3.1. 데이터 소스 카테고리

- **Cloud 데이터 소스**: Google Cloud 내 저장 (예: Cloud Storage 버킷, Cloud SQL DB)
- **외부 데이터 소스**: 온프레미스 또는 타 클라우드 (예: Amazon S3, MS SQL Server)

### 3.2. 저장소 옵션 비교

#### 3.2.1. 데이터베이스 (Database)

체계화된 데이터 컬렉션. 데이터를 **저장·가져오기·사용** 목적.


| 유형                | 제품                              | 특징                                                   |
| --------------------- | ----------------------------------- | -------------------------------------------------------- |
| 관계형 (Relational) | Cloud SQL, Cloud Spanner, AlloyDB | 테이블 조인, SQL 사용, 일관성 높음, 정형 데이터에 적합 |
| 비관계형 (NoSQL)    | Bigtable, Firestore               | 유연한 데이터 모델, 구성이 자주 변경되는 데이터에 적합 |

#### 3.2.2. 데이터 웨어하우스 (Data Warehouse)

- **목적**: 데이터 **분석** 설계
- **데이터 형태**: 정형 + 반정형 데이터
- **Google Cloud 제품**: BigQuery

#### 3.2.3. 데이터 레이크 (Data Lake)

- **목적**: 모든 원시 데이터 유형/볼륨을 원래 형식으로 저장
- 크기 제한 없음
- 전처리 없이 다양한 데이터 저장 가능

> 💡 **Tip**: 데이터 웨어하우스와 데이터 레이크는 **양자택일이 아닌 상호 보완적**인 도구이다.

### 3.3. 데이터 유형과 활용


| 데이터 유형   | 설명                   | 활용                          |
| --------------- | ------------------------ | ------------------------------- |
| 정형 데이터   | 행과 열로 구성         | 통계 분석, 데이터 분석에 최적 |
| 비정형 데이터 | 텍스트, 이미지, 오디오 | 머신러닝(패턴 식별, 예측)     |

---

## 4. BigQuery 소개

### 4.1. BigQuery란?

- **완전 관리형(Fully-managed) 데이터 웨어하우스**
- 인프라 관리 없이 **SQL 쿼리**로 비즈니스 질문에 답할 수 있음

### 4.2. 핵심 특징

#### 4.2.1. 2가지 서비스를 하나로 제공

- 빠른 SQL 쿼리 엔진 (분석)
- 완전 관리형 스토리지 레이어 (저장)

#### 4.2.2. 서버리스(Serverless)

- 리소스 프로비저닝 불필요
- 서버 관리 불필요

#### 4.2.3. 확장성

- TB급 쿼리: 초 단위
- PB급 쿼리: 분 단위
- 실제 사례: 350PB 저장, 10조 행 쿼리, 동시 10,000개 쿼리 실행

#### 4.2.4. 보안

- 저장 데이터 기본 암호화 (별도 조치 불필요)

#### 4.2.5. 가격 모델

- 주문형(On-demand): 처리된 바이트 수 + 스토리지 요금
- 용량 컴퓨팅(Capacity): 고정 월정액

#### 4.2.6. 머신러닝 통합

- **BigQuery ML**: SQL로 ML 모델 작성
- Vertex AI로 데이터셋 직접 내보내기 가능

### 4.3. BigQuery 슬롯(Slot)

- SQL 쿼리 실행을 위한 **가상 CPU**
- 쿼리 크기/복잡성에 따라 자동 계산
- 기본 제공: **2,000개 슬롯**
- 동적 할당: 실제 사용량에 따른 리소스 할당

---

## 5. BigQuery 작동 방식

### 5.1. 아키텍처: 컴퓨팅과 스토리지 분리

- 두 서비스가 **고속 내부 네트워크**로 연결
- 컴퓨팅과 스토리지를 독립적으로 확장 가능

### 5.2. 스토리지 서비스

- 데이터를 **데이터셋(Dataset)** 단위로 정리
- 데이터셋 범위: **Google Cloud 프로젝트**
- 참조 구조: `project.dataset.table`
- 저장 위치: Google 파일 시스템 **Colossus** (고도로 압축된 열 단위)
- **일괄 수집** + **스트리밍 수집** 모두 지원

### 5.3. 쿼리 서비스

실행 방법:

- Google Cloud 콘솔
- BigQuery 웹 UI
- `bq` 명령줄 도구
- REST API (7개 프로그래밍 언어 지원)

### 5.4. 외부 데이터 쿼리

- Cloud Storage의 CSV 파일
- Google Sheets 데이터
- 단, BigQuery는 **자체 스토리지 데이터**에서 가장 효율적으로 작동

### 5.5. 비용 최적화 팁

- 처리하는 **데이터양 제어**가 가장 중요한 비용 절감 방법
- 필요한 열과 행만 선택

```sql
-- ❌ 나쁜 예: 모든 컬럼 선택
SELECT * FROM dataset.table;

-- ✅ 좋은 예: 필요한 컬럼만 선택
SELECT column1, column2 FROM dataset.table
WHERE condition IS NOT NULL
GROUP BY column1
ORDER BY column2
LIMIT 5;
```

---

## 6. BigQuery의 데이터 구성 방식

### 6.1. 계층 구조

```
Project (프로젝트)
  └── Dataset (데이터셋)
        └── Table (테이블)
              └── Column (열)
```

### 6.2. 컬럼 기반 스토리지 (Columnar Storage)

- **행이 아닌 열 단위**로 데이터 처리
- 쿼리 시 **관련 열만 읽기** → 대용량 읽기 최적화
- 동일 유형 데이터로 **압축 효율 ↑**
- 자동 압축, 암호화, 복제

### 6.3. 스키마 설정 방법

- Google Cloud 콘솔에서 **수동 입력**
- **JSON 파일** 제공
- **자동 추론**: Avro, Parquet, ORC, Firestore/Datastore 내보내기 (자기 기술형 파일)

### 6.4. 성능 최적화

- **파티셔닝(Partitioning)**: 액세스 패턴에 따라 분할
- **클러스터링(Clustering)**: 관련 데이터 그룹화
- → 비용 제어 + 쿼리 성능 향상

---

## 7. 핵심 정리

- 7.1. **데이터 분석 수명 주기**는 수집 → 저장 → 처리 → 분석의 반복 프로세스이다.
- 7.2. **BigQuery**는 Google Cloud의 핵심 데이터 웨어하우스 솔루션으로, 서버리스/완전 관리형이다.
- 7.3. **컴퓨팅과 스토리지의 분리**로 유연한 확장이 가능하다.
- 7.4. **컬럼 기반 저장 방식**으로 대용량 분석에 최적화되어 있다.
- 7.5. 비용 최적화의 핵심은 **처리 데이터양 제어**이다.

---
