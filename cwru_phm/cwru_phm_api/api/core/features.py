from dataclasses import dataclass, asdict

import numpy as np
from scipy import fft
from scipy.signal import butter, filtfilt, hilbert

from api.core.fault_freq import FaultFrequencies


# 학습 시 사용한 세그먼트 길이. 추론도 동일해야 함.
SEGMENT_LENGTH = 4096

# 특징 이름 (모델 학습 시와 순서가 동일해야 함)
FEATURE_NAMES = [
    "RMS", "Kurtosis", "Crest", "P2P", "Skewness", "Std",
    "FFT_0_200", "FFT_200_500", "FFT_2k_5k",
    "Env_BPFO", "Env_BPFI", "Env_BSF", "Env_0_200", "Env_200_500",
]


@dataclass
class FeatureBlock:
    """추출된 14개 특징을 도메인별로 묶어서 보관."""
    # 시간 도메인
    RMS: float
    Kurtosis: float
    Crest: float
    P2P: float
    Skewness: float
    Std: float
    # 주파수 도메인 (대역 에너지)
    FFT_0_200: float
    FFT_200_500: float
    FFT_2k_5k: float
    # 포락선 스펙트럼 (결함 주파수 근방 + 저/중주파)
    Env_BPFO: float
    Env_BPFI: float
    Env_BSF: float
    Env_0_200: float
    Env_200_500: float

    def to_vector(self) -> np.ndarray:
        """모델 입력용 1D 벡터. 순서는 FEATURE_NAMES와 일치."""
        return np.array([getattr(self, n) for n in FEATURE_NAMES], dtype=np.float64)

    def to_dict(self) -> dict:
        return asdict(self)


def _band_energy(spectrum: np.ndarray, freqs: np.ndarray, lo: float, hi: float) -> float:
    mask = (freqs >= lo) & (freqs <= hi)
    if not np.any(mask):
        return 0.0
    return float(np.sum(spectrum[mask] ** 2))


def extract_features(
    signal_arr: np.ndarray,
    fs: int,
    fault_freq: FaultFrequencies,
) -> FeatureBlock:
    if len(signal_arr) != SEGMENT_LENGTH:
        raise ValueError(
            f"signal length must be {SEGMENT_LENGTH}, got {len(signal_arr)}"
        )

    x = np.asarray(signal_arr, dtype=np.float64)
    N = len(x)

    # 시간 도메인 특징
    mean_x = np.mean(x)
    std_x = np.std(x)
    rms = float(np.sqrt(np.mean(x ** 2)))
    eps = 1e-12
    kurtosis = float(np.mean((x - mean_x) ** 4) / (std_x ** 4 + eps))
    skewness = float(np.mean((x - mean_x) ** 3) / (std_x ** 3 + eps))
    crest = float(np.max(np.abs(x)) / (rms + eps))
    p2p = float(np.max(x) - np.min(x))

    # 주파수 도메인 (raw FFT 대역 에너지)
    freqs = fft.rfftfreq(N, 1.0 / fs)
    fft_mag = np.abs(fft.rfft(x)) / (N / 2.0)
    fft_0_200 = _band_energy(fft_mag, freqs, 0, 200)
    fft_200_500 = _band_energy(fft_mag, freqs, 200, 500)
    fft_2k_5k = _band_energy(fft_mag, freqs, 2000, 5000)

    # 포락선 스펙트럼
    # 베어링 공진 대역(2~5kHz)을 BPF로 추출 -> 힐버트 포락선 -> FFT
    try:
        b, a = butter(4, [2000, 5000], btype="band", fs=fs)
        x_bp = filtfilt(b, a, x)
        envelope = np.abs(hilbert(x_bp))
        env_fft = np.abs(fft.rfft(envelope - np.mean(envelope))) / (N / 2.0)
    except Exception:
        env_fft = np.zeros_like(fft_mag)

    # 결함 주파수 근방 +-5Hz 윈도우의 에너지
    env_bpfo = _band_energy(env_fft, freqs, fault_freq.BPFO - 5, fault_freq.BPFO + 5)
    env_bpfi = _band_energy(env_fft, freqs, fault_freq.BPFI - 5, fault_freq.BPFI + 5)
    env_bsf = _band_energy(env_fft, freqs, fault_freq.two_BSF - 5, fault_freq.two_BSF + 5)
    # 저/중주파 대역 에너지
    env_0_200 = _band_energy(env_fft, freqs, 0, 200)
    env_200_500 = _band_energy(env_fft, freqs, 200, 500)

    return FeatureBlock(
        RMS=rms, Kurtosis=kurtosis, Crest=crest, P2P=p2p,
        Skewness=skewness, Std=float(std_x),
        FFT_0_200=fft_0_200, FFT_200_500=fft_200_500, FFT_2k_5k=fft_2k_5k,
        Env_BPFO=env_bpfo, Env_BPFI=env_bpfi, Env_BSF=env_bsf,
        Env_0_200=env_0_200, Env_200_500=env_200_500,
    )
