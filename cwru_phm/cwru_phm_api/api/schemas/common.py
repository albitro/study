from pydantic import BaseModel, Field


class TimeFeatures(BaseModel):
    RMS: float
    Kurtosis: float
    Crest: float
    P2P: float
    Skewness: float
    Std: float


class FreqFeatures(BaseModel):
    FFT_0_200: float
    FFT_200_500: float
    FFT_2k_5k: float


class EnvelopeFeatures(BaseModel):
    Env_BPFO: float
    Env_BPFI: float
    Env_BSF: float
    Env_0_200: float
    Env_200_500: float


class FeatureBlockOut(BaseModel):
    time_domain: TimeFeatures
    freq_domain: FreqFeatures
    envelope: EnvelopeFeatures


class FaultFrequenciesOut(BaseModel):
    rpm: float
    fr: float = Field(description="회전 주파수 (RPM/60)")
    BPFO: float = Field(description="외륜 결함 주파수")
    BPFI: float = Field(description="내륜 결함 주파수")
    BSF: float = Field(description="볼 자전 주파수")
    two_BSF: float = Field(description="볼 결함 충격 주파수 (= 2*BSF)")
    FTF: float = Field(description="케이지 회전 주파수")


class DiagnosisOut(BaseModel):
    dominant_peak_hz: float = Field(
        description="포락선 스펙트럼에서 가장 강한 피크 주파수 [Hz]"
    )
    dominant_peak_amp: float
    snr: float = Field(description="노이즈 플로어 대비 피크의 비율 (배수)")
    nearest_fault: str | None = Field(
        default=None,
        description="가장 가까운 결함 주파수 이름 (BPFO/BPFI/2*BSF). 매칭이 없으면 null",
    )
    nearest_fault_freq_hz: float | None = None
    delta_hz: float | None = Field(
        default=None,
        description="검출 피크와 이론값의 차이 [Hz]",
    )
