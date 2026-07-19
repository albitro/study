import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

ANALOG_SENSORS: list[str] = [
    "TP2",              # 압축기 공기 압력 (bar)
    "TP3",              # 패널 공기 압력 (bar)
    "H1",               # 토출 밸브 압력 (bar)
    "DV_pressure",      # 토출 밸브 내부 압력 (bar)
    "Reservoirs",       # 저장조 공기 압력 (bar)
    "Oil_temperature",  # 오일 온도 (섭씨)
    "Motor_current",    # 모터 전류 (A)
]

DIGITAL_SENSORS: list[str] = [
    "COMP", "DV_eletric", "Towers", "MPG",
    "LPS", "Pressure_switch", "Oil_level", "Caudal_impulses",
]


@dataclass(frozen=True)
class FailureWindow:
    start: pd.Timestamp
    end: pd.Timestamp
    failure_type: str
    description: str


FAILURE_WINDOWS: list[FailureWindow] = [
    FailureWindow(
        pd.Timestamp("2020-04-12 11:50:00"),
        pd.Timestamp("2020-04-12 23:30:00"),
        "Air Leak",
        "토출부 공기 누설로 압력 회복 불가, 압축기 과작동",
    ),
    FailureWindow(
        pd.Timestamp("2020-04-18 00:00:00"),
        pd.Timestamp("2020-04-18 23:59:00"),
        "Air Leak",
        "지속적 공기 누설, TP2/TP3 동시 이상",
    ),
    FailureWindow(
        pd.Timestamp("2020-05-29 23:30:00"),
        pd.Timestamp("2020-05-30 06:00:00"),
        "Air Leak",
        "야간 운전 중 공기 누설 발생",
    ),
    FailureWindow(
        pd.Timestamp("2020-06-05 10:00:00"),
        pd.Timestamp("2020-06-07 14:30:00"),
        "Air Leak",
        "장기간 누설, 모터 전류 상승",
    ),
    FailureWindow(
        pd.Timestamp("2020-07-15 14:30:00"),
        pd.Timestamp("2020-07-15 19:00:00"),
        "Oil Leak",
        "오일 누설 의심, 오일 온도 비정상 패턴",
    ),
]


def _resolve_csv_path(data_dir: str | Path) -> Path:
    data_dir = Path(data_dir)
    candidates = list(data_dir.glob("*.csv"))
    if not candidates:
        raise FileNotFoundError(
            f"MetroPT-3 CSV not found in {data_dir}. "
            "https://archive.ics.uci.edu/dataset/791 에서 다운로드 후 배치하세요."
        )

    for c in candidates:
        if "metro" in c.name.lower():
            return c
    return candidates[0]


def load_metropt3(
    data_dir: str | Path = "data/metropt3",
    parse_time: bool = True,
    downsample: str | None = "1min",
) -> pd.DataFrame:
    csv_path = _resolve_csv_path(data_dir)
    df = pd.read_csv(csv_path)

    drop_cols = [c for c in df.columns if str(c).startswith("Unnamed")]
    if drop_cols:
        df = df.drop(columns=drop_cols)

    ts_col = next((c for c in df.columns if c.lower() in ("timestamp", "time", "datetime")), None)
    if ts_col is None:
        raise ValueError(f"timestamp column not found in {df.columns.tolist()}")

    if parse_time:
        df[ts_col] = pd.to_datetime(df[ts_col])
        df = df.set_index(ts_col).sort_index()

    df["label"] = _label_from_windows(df.index, FAILURE_WINDOWS)

    if downsample:
        agg = {c: "mean" for c in df.columns if c != "label"}
        agg["label"] = "max"
        df = df.resample(downsample).agg(agg).dropna()

    return df


def _label_from_windows(idx: pd.DatetimeIndex, windows: Iterable[FailureWindow]) -> np.ndarray:
    label = np.zeros(len(idx), dtype=np.int8)
    for w in windows:
        mask = (idx >= w.start) & (idx <= w.end)
        label[mask] = 1
    return label


EQUIPMENT_REGISTRY: dict[str, dict] = {
    "APU-01": {
        "name": "1호 APU 압축기",
        "location": "Line A 차량기지",
        "time_offset_days": 0,
    },
    "APU-02": {
        "name": "2호 APU 압축기",
        "location": "Line B 차량기지",
        "time_offset_days": 30,
    },
    "APU-03": {
        "name": "3호 APU 압축기",
        "location": "Line C 차량기지",
        "time_offset_days": 60,
    },
}


class SensorDB:
    def __init__(self, df: pd.DataFrame | None = None, data_dir: str | Path = "data/metropt3"):
        self._df = df if df is not None else load_metropt3(data_dir=data_dir)

    @property
    def equipment_ids(self) -> list[str]:
        return list(EQUIPMENT_REGISTRY.keys())

    def info(self, equipment_id: str) -> dict:
        if equipment_id not in EQUIPMENT_REGISTRY:
            raise KeyError(f"unknown equipment_id: {equipment_id}")
        return EQUIPMENT_REGISTRY[equipment_id] | {"id": equipment_id}

    def query(
        self,
        equipment_id: str,
        start: str | datetime | pd.Timestamp,
        end: str | datetime | pd.Timestamp,
        sensors: list[str] | None = None,
    ) -> pd.DataFrame:
        info = self.info(equipment_id)
        offset = pd.Timedelta(days=info["time_offset_days"])

        start_internal = pd.Timestamp(start) - offset
        end_internal = pd.Timestamp(end) - offset

        cols = sensors if sensors else ANALOG_SENSORS + ["label"]
        cols = [c for c in cols if c in self._df.columns]

        sliced = self._df.loc[start_internal:end_internal, cols].copy()

        sliced.index = sliced.index + offset
        return sliced

    def latest(
        self,
        equipment_id: str,
        hours: int = 24,
        sensors: list[str] | None = None,
    ) -> pd.DataFrame:
        info = self.info(equipment_id)
        offset = pd.Timedelta(days=info["time_offset_days"])
        end_internal = self._df.index.max()
        start_internal = end_internal - pd.Timedelta(hours=hours)
        return self.query(
            equipment_id,
            start_internal + offset,
            end_internal + offset,
            sensors,
        )


def make_windows(
    df: pd.DataFrame,
    window: int = 60,
    stride: int = 30,
    sensor_cols: list[str] | None = None,
    label_col: str = "label",
) -> tuple[np.ndarray, np.ndarray]:
    sensor_cols = sensor_cols or ANALOG_SENSORS
    sensor_cols = [c for c in sensor_cols if c in df.columns]
    arr = df[sensor_cols].to_numpy(dtype=np.float32)
    labels = df[label_col].to_numpy(dtype=np.int8) if label_col in df.columns else np.zeros(len(df))

    xs, ys = [], []
    for i in range(0, len(arr) - window + 1, stride):
        xs.append(arr[i:i + window])
        ys.append(int(labels[i:i + window].max()))
    return np.stack(xs), np.array(ys, dtype=np.int8)
