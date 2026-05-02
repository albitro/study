import argparse
import sys
from pathlib import Path

import httpx
import numpy as np
from scipy.io import loadmat

SEGMENT_LENGTH = 4096


def load_de_signal(filepath: Path) -> np.ndarray:
    mat = loadmat(str(filepath))
    de_keys = [k for k in mat.keys() if "DE_time" in k]
    if not de_keys:
        raise ValueError(f"No DE_time key in {filepath}")
    if len(de_keys) > 1:
        code = filepath.stem.split("_")[-1]
        matched = [k for k in de_keys if code in k]
        if matched:
            de_keys = matched
    return mat[de_keys[0]].flatten()


def main():
    parser = argparse.ArgumentParser(description="CWRU PHM API test client")
    parser.add_argument("matfile", type=Path, help="CWRU .mat file path")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--rpm", type=float, default=1772.0)
    parser.add_argument("--fs", type=int, default=12000)
    parser.add_argument("--n", type=int, default=3, help="number of segments to send")
    args = parser.parse_args()

    if not args.matfile.exists():
        print(f"File not found: {args.matfile}", file=sys.stderr)
        sys.exit(1)

    # 헬스체크
    try:
        r = httpx.get(f"{args.url}/health", timeout=5.0)
        r.raise_for_status()
        print(f"Server OK: {r.json()}")
    except Exception as e:
        print(f"Server not reachable: {e}", file=sys.stderr)
        sys.exit(1)

    # 신호 로드
    signal_arr = load_de_signal(args.matfile)
    n_segments = min(args.n, len(signal_arr) // SEGMENT_LENGTH)
    print(f"\nLoaded {len(signal_arr)} samples → {n_segments} segments to send\n")

    # 각 세그먼트 전송
    summary = []
    with httpx.Client(timeout=10.0) as client:
        for i in range(n_segments):
            seg = signal_arr[i * SEGMENT_LENGTH : (i + 1) * SEGMENT_LENGTH]
            payload = {
                "signal": seg.tolist(),
                "fs": args.fs,
                "rpm": args.rpm,
            }
            r = client.post(f"{args.url}/predict", json=payload)
            if r.status_code != 200:
                print(f"  [{i}] FAILED: {r.status_code} {r.text[:200]}")
                continue

            data = r.json()
            label = data["prediction"]["label"]
            probs = data["prediction"]["probabilities"]
            top_p = probs[label]
            rms = data["features"]["time_domain"]["RMS"]
            kurt = data["features"]["time_domain"]["Kurtosis"]
            peak = data["diagnosis"]["dominant_peak_hz"]
            nearest = data["diagnosis"]["nearest_fault"]
            snr = data["diagnosis"]["snr"]
            ms = data["meta"]["inference_ms"]

            print(
                f"  [{i}] {label:7s} ({top_p:.2%}) | "
                f"RMS={rms:.3f} Kurt={kurt:.1f} | "
                f"peak={peak:.1f}Hz ({nearest}, SNR {snr:.1f}x) | {ms:.1f}ms"
            )
            summary.append(label)

    # 다수결 투표 요약
    if summary:
        from collections import Counter
        counter = Counter(summary)
        majority, count = counter.most_common(1)[0]
        print(f"\nMajority vote: {majority} ({count}/{len(summary)})")


if __name__ == "__main__":
    main()
