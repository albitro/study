import argparse
import json
import sys
from pathlib import Path

import numpy as np


SEGMENT_LENGTH = 4096
DEFAULT_FS = 12000
DEFAULT_RPM = 1772.0


def make_synthetic_signal(kind: str, fs: int, rpm: float) -> np.ndarray:
    # 기존 프로젝트와 동일한 베어링 스펙으로 결함 주파수 계산
    fr = rpm / 60.0
    n_balls, bd, pd = 9, 7.938, 39.04
    ratio = bd / pd
    bpfo = (n_balls / 2.0) * fr * (1.0 - ratio)
    bpfi = (n_balls / 2.0) * fr * (1.0 + ratio)
    two_bsf = 2.0 * (pd / (2.0 * bd)) * fr * (1.0 - ratio ** 2)

    np.random.seed(42)

    if kind == "normal":
        # 정상: 작은 진폭의 백색잡음만
        return np.random.randn(SEGMENT_LENGTH) * 0.07

    # 결함 시뮬레이션: 결함 주파수마다 3kHz 공진 충격을 주입
    fault_hz = {"inner": bpfi, "outer": bpfo, "ball": two_bsf}[kind]
    period_samp = int(fs / fault_hz)

    sig = np.zeros(SEGMENT_LENGTH)
    for start in range(0, SEGMENT_LENGTH, period_samp):
        L = min(SEGMENT_LENGTH - start, period_samp)
        tau = np.arange(L) / fs
        # 3kHz 공진을 200/s로 감쇠시키는 충격
        impact = np.sin(2 * np.pi * 3000 * tau) * np.exp(-200 * tau)
        sig[start:start + L] += impact

    # 진폭 조정 + 노이즈
    return sig * 2.0 + np.random.randn(SEGMENT_LENGTH) * 0.05


def load_mat_segment(matfile: Path, segment_index: int = 0) -> np.ndarray:
    from scipy.io import loadmat

    mat = loadmat(str(matfile))
    de_keys = [k for k in mat.keys() if "DE_time" in k]
    if not de_keys:
        raise ValueError(f"No DE_time key found in {matfile}")

    # IR014처럼 채널이 여러 개면 파일명 코드와 매칭
    if len(de_keys) > 1:
        code = matfile.stem.split("_")[-1]
        matched = [k for k in de_keys if code in k]
        if matched:
            de_keys = matched

    full_signal = mat[de_keys[0]].flatten()
    start = segment_index * SEGMENT_LENGTH
    end = start + SEGMENT_LENGTH

    if end > len(full_signal):
        raise ValueError(
            f"Signal too short: needs {end} samples, got {len(full_signal)}"
        )

    return full_signal[start:end]


def write_payload(signal_arr: np.ndarray, fs: int, rpm: float, output: Path) -> None:
    payload = {
        "signal": signal_arr.tolist(),
        "fs": fs,
        "rpm": rpm,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        json.dump(payload, f)

    size_kb = output.stat().st_size / 1024
    print(f"  Wrote {len(signal_arr)} samples to {output} ({size_kb:.1f} KB)")
    print(f"    fs  = {fs}, rpm = {rpm}")
    print(f"    RMS = {float(np.sqrt(np.mean(signal_arr ** 2))):.4f}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate /predict payload as JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    # synthetic 서브커맨드
    p_syn = sub.add_parser("synthetic", help="합성 신호 생성")
    p_syn.add_argument(
        "kind", choices=["normal", "inner", "outer", "ball"],
        help="시뮬레이션할 베어링 상태",
    )
    p_syn.add_argument("--output", type=Path, default=None)
    p_syn.add_argument("--fs", type=int, default=DEFAULT_FS)
    p_syn.add_argument("--rpm", type=float, default=DEFAULT_RPM)

    # matfile 서브커맨드
    p_mat = sub.add_parser("matfile", help=".mat 파일에서 페이로드 추출")
    p_mat.add_argument("matfile", type=Path, help="CWRU .mat 파일 경로")
    p_mat.add_argument("--segment", type=int, default=0, help="몇 번째 4096 세그먼트")
    p_mat.add_argument("--output", type=Path, default=None)
    p_mat.add_argument("--fs", type=int, default=DEFAULT_FS)
    p_mat.add_argument("--rpm", type=float, default=DEFAULT_RPM)

    args = parser.parse_args()

    if args.mode == "synthetic":
        signal_arr = make_synthetic_signal(args.kind, args.fs, args.rpm)
        output = args.output or Path(f"./examples/{args.kind}.json")
    else:
        if not args.matfile.exists():
            print(f"File not found: {args.matfile}", file=sys.stderr)
            sys.exit(1)
        signal_arr = load_mat_segment(args.matfile, args.segment)
        output = args.output or Path(f"./examples/{args.matfile.stem}_seg{args.segment}.json")

    write_payload(signal_arr, fs=args.fs, rpm=args.rpm, output=output)


if __name__ == "__main__":
    main()
