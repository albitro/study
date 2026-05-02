from dataclasses import dataclass
from typing import Optional

import numpy as np
from scipy import fft
from scipy.signal import butter, filtfilt, hilbert

from api.core.fault_freq import FaultFrequencies


@dataclass
class DiagnosisInfo:
    dominant_peak_hz: float           # 포락선 스펙트럼에서 가장 강한 피크 주파수
    dominant_peak_amp: float          # 그 피크의 진폭
    snr: float                        # 노이즈 플로어 대비 피크의 비율 (배수)
    nearest_fault: Optional[str]      # 가장 가까운 결함 주파수 이름 (BPFO/BPFI/2*BSF)
    nearest_fault_freq_hz: Optional[float]   # 그 결함 주파수의 이론값
    delta_hz: Optional[float]         # 검출 피크와 이론값의 차이

    def to_dict(self) -> dict:
        return {
            "dominant_peak_hz": self.dominant_peak_hz,
            "dominant_peak_amp": self.dominant_peak_amp,
            "snr": self.snr,
            "nearest_fault": self.nearest_fault,
            "nearest_fault_freq_hz": self.nearest_fault_freq_hz,
            "delta_hz": self.delta_hz,
        }


def _envelope_spectrum(x: np.ndarray, fs: int) -> tuple[np.ndarray, np.ndarray]:
    N = len(x)
    freqs = fft.rfftfreq(N, 1.0 / fs)
    try:
        b, a = butter(4, [2000, 5000], btype="band", fs=fs)
        x_bp = filtfilt(b, a, x)
        envelope = np.abs(hilbert(x_bp))
        env_fft = np.abs(fft.rfft(envelope - np.mean(envelope))) / (N / 2.0)
    except Exception:
        env_fft = np.zeros_like(freqs)
    return freqs, env_fft


def diagnose(
    signal_arr: np.ndarray,
    fs: int,
    fault_freq: FaultFrequencies,
    search_range_hz: tuple[float, float] = (10.0, 500.0),
    match_tolerance_hz: float = 5.0,
) -> DiagnosisInfo:
    x = np.asarray(signal_arr, dtype=np.float64)
    freqs, env_fft = _envelope_spectrum(x, fs)

    # 검색 범위로 마스킹
    lo, hi = search_range_hz
    search_mask = (freqs >= lo) & (freqs <= hi)

    if not np.any(search_mask) or np.all(env_fft[search_mask] == 0):
        # 신호에 문제가 있으면 빈 진단
        return DiagnosisInfo(
            dominant_peak_hz=0.0, dominant_peak_amp=0.0, snr=0.0,
            nearest_fault=None, nearest_fault_freq_hz=None, delta_hz=None,
        )

    # 검색 범위 안에서 가장 큰 피크
    search_freqs = freqs[search_mask]
    search_amps = env_fft[search_mask]
    peak_idx_local = int(np.argmax(search_amps))
    peak_freq = float(search_freqs[peak_idx_local])
    peak_amp = float(search_amps[peak_idx_local])

    # SNR: peak 진폭 / 나머지 영역의 평균 진폭
    # peak 주변 ±5Hz는 제외하고 노이즈 플로어 계산
    noise_mask = search_mask & ((freqs < peak_freq - 5) | (freqs > peak_freq + 5))
    noise_floor = float(np.mean(env_fft[noise_mask])) if np.any(noise_mask) else 1e-12
    snr = peak_amp / (noise_floor + 1e-12)

    # 가장 가까운 결함 주파수 매칭
    candidates = {
        "BPFO": fault_freq.BPFO,
        "BPFI": fault_freq.BPFI,
        "2*BSF": fault_freq.two_BSF,
    }
    nearest_name, nearest_val = min(
        candidates.items(), key=lambda kv: abs(kv[1] - peak_freq)
    )
    delta = peak_freq - nearest_val

    if abs(delta) <= match_tolerance_hz:
        return DiagnosisInfo(
            dominant_peak_hz=peak_freq,
            dominant_peak_amp=peak_amp,
            snr=snr,
            nearest_fault=nearest_name,
            nearest_fault_freq_hz=nearest_val,
            delta_hz=delta,
        )
    else:
        # 어떤 결함 주파수와도 가깝지 않음 → 정상이거나 다른 원인
        return DiagnosisInfo(
            dominant_peak_hz=peak_freq,
            dominant_peak_amp=peak_amp,
            snr=snr,
            nearest_fault=None,
            nearest_fault_freq_hz=None,
            delta_hz=None,
        )
