from dataclasses import dataclass


# SKF 6205-2RS JEM 베어링 스펙 (CWRU 공식 페이지 기준)
N_BALLS = 9         # 볼 개수
BD = 7.938          # 볼 직경 [mm]
PD = 39.04          # 피치 직경 [mm]


@dataclass
class FaultFrequencies:
    rpm: float      # 입력 회전 속도
    fr: float       # 회전 주파수 (RPM/60)
    BPFO: float     # 외륜 결함
    BPFI: float     # 내륜 결함
    BSF: float      # 볼 자전 (실제 충격은 2*BSF)
    FTF: float      # 케이지

    @property
    def two_BSF(self) -> float:
        return 2.0 * self.BSF

    def to_dict(self) -> dict:
        return {
            "rpm": self.rpm,
            "fr": self.fr,
            "BPFO": self.BPFO,
            "BPFI": self.BPFI,
            "BSF": self.BSF,
            "two_BSF": self.two_BSF,
            "FTF": self.FTF,
        }


def compute_fault_frequencies(rpm: float) -> FaultFrequencies:
    fr = rpm / 60.0
    ratio = BD / PD

    bpfo = (N_BALLS / 2.0) * fr * (1.0 - ratio)
    bpfi = (N_BALLS / 2.0) * fr * (1.0 + ratio)
    bsf = (PD / (2.0 * BD)) * fr * (1.0 - ratio ** 2)
    ftf = (fr / 2.0) * (1.0 - ratio)

    return FaultFrequencies(rpm=rpm, fr=fr, BPFO=bpfo, BPFI=bpfi, BSF=bsf, FTF=ftf)
