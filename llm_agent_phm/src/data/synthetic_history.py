from __future__ import annotations

from pathlib import Path

import pandas as pd


HISTORY_RECORDS: list[dict] = [
    # APU-01
    {
        "case_id": "INC-2020-0317",
        "date": "2020-03-17 10:20",
        "equipment_id": "APU-01",
        "symptom": "정기 점검 중 H1 압력 노이즈 증가 발견, 운전엔 영향 없음",
        "diagnosis": "센서 드리프트 (Sensor Drift)",
        "root_cause": "압력 센서 노후 (사용 시간 25,000h 초과)",
        "action": "센서 신품 교체 및 영점 보정",
        "downtime_min": 25,
        "technician": "김OO",
    },
    {
        "case_id": "INC-2020-0405",
        "date": "2020-04-05 09:30",
        "equipment_id": "APU-01",
        "symptom": "TP2가 8.5bar에서 회복 지연, 무부하 시간 평소 대비 30% 단축",
        "diagnosis": "공기 누설 초기 (Air Leak — Minor)",
        "root_cause": "토출 밸브 후단 O-ring 미세 누설",
        "action": "O-ring 교체 권고했으나 운전 지속, 1주 후 재발 우려",
        "downtime_min": 30,
        "technician": "김OO",
    },
    {
        "case_id": "INC-2020-0712",
        "date": "2020-07-12 16:40",
        "equipment_id": "APU-01",
        "symptom": "Oil_temperature 78°C 도달, Oil_level 신호 미세 변동 관찰",
        "diagnosis": "오일 누설 전조 (Oil Leak — Suspect)",
        "root_cause": "크랭크케이스 드레인 플러그 미세 풀림",
        "action": "플러그 토크 재조임, 오일 0.5L 보충, 모니터링 강화 권고",
        "downtime_min": 35,
        "technician": "이OO",
    },
    # APU-02
    {
        "case_id": "INC-2020-0508",
        "date": "2020-05-08 03:15",
        "equipment_id": "APU-02",
        "symptom": "야간 무부하 운전 중 TP3 압력 7.2 → 5.8bar 저하 반복",
        "diagnosis": "공기 누설 (Air Leak)",
        "root_cause": "Reservoirs 라인 플랜지 가스켓 균열",
        "action": "가스켓 신규 교체, 플랜지 토크 재조정, 누설 시험 통과",
        "downtime_min": 120,
        "technician": "박OO",
    },
    {
        "case_id": "INC-2020-0701",
        "date": "2020-07-01 11:45",
        "equipment_id": "APU-02",
        "symptom": "Motor_current 피크가 정상 5.2A 대비 7.8A까지 상승, 압력 회복 시간 증가",
        "diagnosis": "공기 누설 + 압축기 부하 증가",
        "root_cause": "흡기 필터 부분 막힘 + DV 솔레노이드 응답 지연 의심",
        "action": "흡기 필터 교체, 솔레노이드 코일 측정, 부분 정상화",
        "downtime_min": 50,
        "technician": "최OO",
    },
    # APU-03
    {
        "case_id": "INC-2020-0607",
        "date": "2020-06-07 03:00",
        "equipment_id": "APU-03",
        "symptom": "압축기 기동 후 8bar 도달까지 평소 60초 → 145초로 지연",
        "diagnosis": "공기 누설 + 밸브 이상 의심",
        "root_cause": "DV(토출 밸브) 솔레노이드 동작 불량 + 라인 미세 누설",
        "action": "솔레노이드 교체, 누설 부위 실링, 통합 시험 정상",
        "downtime_min": 180,
        "technician": "정OO",
    },
    {
        "case_id": "INC-2020-0801",
        "date": "2020-08-01 22:40",
        "equipment_id": "APU-03",
        "symptom": "야간 운전 중 TP2 변동폭 ±0.8bar 관찰, Reservoirs 동반 저하",
        "diagnosis": "공기 누설 재발 (Air Leak — Recurring)",
        "root_cause": "이전 보수(INC-2020-0607) 부위 인접 가스켓 추가 노후",
        "action": "동일 라인 가스켓 일괄 교체, 토크 재조정",
        "downtime_min": 95,
        "technician": "정OO",
    },
    {
        "case_id": "INC-2020-0910",
        "date": "2020-09-10 06:00",
        "equipment_id": "APU-03",
        "symptom": "Oil_level LOW 알람, 운전 자동 정지",
        "diagnosis": "오일 누설 (Oil Leak)",
        "root_cause": "크랭크케이스 하단 드레인 플러그 풀림",
        "action": "오일 보충, 드레인 플러그 토크 조임, 누설 모니터링 1주",
        "downtime_min": 60,
        "technician": "강OO",
    },
]


def build_history_df() -> pd.DataFrame:
    df = pd.DataFrame(HISTORY_RECORDS)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


def to_text_records(df: pd.DataFrame) -> list[dict]:
    records = []
    for _, r in df.iterrows():
        text = (
            f"[사례 {r['case_id']}] {r['date'].strftime('%Y-%m-%d %H:%M')} | 설비: {r['equipment_id']}\n"
            f"증상: {r['symptom']}\n"
            f"진단: {r['diagnosis']}\n"
            f"근본 원인: {r['root_cause']}\n"
            f"조치: {r['action']}\n"
            f"다운타임: {r['downtime_min']}분 / 작업자: {r['technician']}"
        )
        records.append({
            "id": r["case_id"],
            "text": text,
            "metadata": {
                "equipment_id": r["equipment_id"],
                "diagnosis": r["diagnosis"],
                "date": r["date"].isoformat(),
            },
        })
    return records


def save_csv(out_path: str | Path = "data/history/failure_history.csv") -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = build_history_df()
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    return out_path


if __name__ == "__main__":
    path = save_csv()
    print(f"saved: {path} (rows={len(build_history_df())})")
