import argparse
import gc
import json
import sys
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
from scipy.io import loadmat
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import KFold, train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api.core.fault_freq import compute_fault_frequencies
from api.core.features import (
    FEATURE_NAMES,
    SEGMENT_LENGTH,
    extract_features,
)


# 학습에 사용할 파일 매핑
DATA_FILES = {
    "Normal":  "Time_Normal_1_098.mat",
    "IR007":   "IR007_1_110.mat",
    "IR014":   "IR014_1_175.mat",
    "IR021":   "IR021_1_214.mat",
    "OR007":   "OR007_6_1_136.mat",
    "OR014":   "OR014_6_1_202.mat",
    "OR021":   "OR021_6_1_239.mat",
    "Ball007": "B007_1_123.mat",
    "Ball014": "B014_1_190.mat",
    "Ball021": "B021_1_227.mat",
}

# 4클래스 분류로 매핑
LABEL_MAP = {
    "Normal":  0,
    "IR007":   1, "IR014":   1, "IR021":   1,
    "OR007":   2, "OR014":   2, "OR021":   2,
    "Ball007": 3, "Ball014": 3, "Ball021": 3,
}
CLASS_NAMES = ["Normal", "Inner", "Outer", "Ball"]


FS = 12000              # 샘플링 주파수
DEFAULT_RPM = 1772      # 대표값 (파일별 1771~1774 편차는 무시)
MAX_SAMPLES = 60000     # 메모리 절약을 위해 파일당 최대 5초만 사용


def load_cwru_mat(filepath: Path, max_n: int = MAX_SAMPLES) -> np.ndarray:
    mat = loadmat(str(filepath))
    de_keys = [k for k in mat.keys() if "DE_time" in k and not k.startswith("__")]

    if not de_keys:
        raise ValueError(f"No DE_time key found in {filepath}")

    # IR014_1_175.mat은 X175_DE_time과 X217_DE_time 두 개를 가지고 있음
    # 파일명의 숫자 코드와 매칭되는 것을 우선 사용
    if len(de_keys) > 1:
        code = filepath.stem.split("_")[-1]
        matched = [k for k in de_keys if code in k]
        if matched:
            de_keys = matched

    data = mat[de_keys[0]].flatten()[:max_n]
    del mat
    gc.collect()
    return data


def load_all_signals(data_dir: Path) -> dict[str, np.ndarray]:
    signals = {}
    missing = []

    for label, filename in DATA_FILES.items():
        filepath = data_dir / filename
        if not filepath.exists():
            missing.append(filename)
            continue
        signals[label] = load_cwru_mat(filepath)

    if missing:
        raise FileNotFoundError(
            f"다음 파일이 {data_dir}에 없습니다:\n  - "
            + "\n  - ".join(missing)
            + "\n\nCWRU Bearing Data Center에서 다운로드하여 data/raw/ 폴더에 넣어주세요."
            + "\nhttps://engineering.case.edu/bearingdatacenter"
        )

    return signals


def build_dataset(
    signals: dict[str, np.ndarray],
    rpm: float,
) -> tuple[np.ndarray, np.ndarray]:
    fault_freq = compute_fault_frequencies(rpm)
    X_list, y_list = [], []

    for label, signal_arr in signals.items():
        class_id = LABEL_MAP[label]
        n_segments = len(signal_arr) // SEGMENT_LENGTH

        for i in range(n_segments):
            seg = signal_arr[i * SEGMENT_LENGTH : (i + 1) * SEGMENT_LENGTH]
            feats = extract_features(seg, fs=FS, fault_freq=fault_freq)
            X_list.append(feats.to_vector())
            y_list.append(class_id)

    X = np.array(X_list)
    y = np.array(y_list)
    return X, y


def train_and_evaluate(
    X: np.ndarray,
    y: np.ndarray,
    random_state: int = 42,
) -> tuple[RandomForestClassifier, dict]:
    print(f"\n  Total samples: {len(y)}")
    for c in range(4):
        print(f"    {CLASS_NAMES[c]:8s}: {int(np.sum(y == c))}")

    # Hold-out 7:3 분할 평가
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.3, random_state=random_state, stratify=y
    )
    clf = RandomForestClassifier(n_estimators=100, random_state=random_state)
    clf.fit(X_tr, y_tr)
    holdout_acc = float(np.mean(clf.predict(X_te) == y_te))
    print(f"\n  Hold-out accuracy: {holdout_acc:.4f}")
    print(classification_report(y_te, clf.predict(X_te), target_names=CLASS_NAMES))

    # 5-Fold Cross Validation
    kf = KFold(n_splits=5, shuffle=True, random_state=random_state)
    fold_accs = []
    for fold_idx, (tri, tei) in enumerate(kf.split(X)):
        c = RandomForestClassifier(n_estimators=100, random_state=random_state)
        c.fit(X[tri], y[tri])
        acc = float(np.mean(c.predict(X[tei]) == y[tei]))
        fold_accs.append(acc)
        print(f"  Fold {fold_idx + 1}: {acc:.4f}")
    cv_mean = float(np.mean(fold_accs))
    cv_std = float(np.std(fold_accs))
    print(f"  CV mean: {cv_mean:.4f} ± {cv_std:.4f}")

    # 최종 모델은 전체 데이터로 다시 학습
    final_clf = RandomForestClassifier(n_estimators=100, random_state=random_state)
    final_clf.fit(X, y)

    metrics = {
        "holdout_accuracy": holdout_acc,
        "cv_mean": cv_mean,
        "cv_std": cv_std,
        "cv_folds": fold_accs,
        "confusion_matrix": confusion_matrix(y_te, clf.predict(X_te)).tolist(),
        "n_samples": int(len(y)),
        "n_per_class": {CLASS_NAMES[c]: int(np.sum(y == c)) for c in range(4)},
    }
    return final_clf, metrics


def save_model(
    model: RandomForestClassifier,
    metrics: dict,
    output_path: Path,
    rpm: float,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
    print(f"\n  Model saved to {output_path}")

    # 메타데이터는 JSON으로 저장
    meta_path = output_path.with_suffix(".meta.json")
    meta = {
        "model_version": output_path.stem,
        "trained_at": datetime.utcnow().isoformat() + "Z",
        "trained_rpm": rpm,
        "fs": FS,
        "segment_length": SEGMENT_LENGTH,
        "feature_names": FEATURE_NAMES,
        "class_names": CLASS_NAMES,
        "metrics": metrics,
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"  Metadata saved to {meta_path}")


def main():
    parser = argparse.ArgumentParser(description="Train CWRU PHM model")
    parser.add_argument(
        "--data-dir", type=Path, default=Path("./data/raw"),
        help="CWRU .mat 파일들이 있는 폴더",
    )
    parser.add_argument(
        "--output", type=Path, default=Path("./models/rf_v1.joblib"),
        help="저장할 모델 파일 경로",
    )
    parser.add_argument(
        "--rpm", type=float, default=DEFAULT_RPM,
        help="학습 데이터의 대표 RPM",
    )
    args = parser.parse_args()

    print("=" * 55)
    print("  CWRU Bearing Fault Classifier - Training")
    print("=" * 55)
    print(f"  Data dir : {args.data_dir.resolve()}")
    print(f"  Output   : {args.output.resolve()}")
    print(f"  RPM      : {args.rpm}")

    # 결함 주파수 출력 (디버깅용)
    ff = compute_fault_frequencies(args.rpm)
    print(f"\n  Fault frequencies @ {args.rpm} RPM:")
    print(f"    BPFO  = {ff.BPFO:.2f} Hz")
    print(f"    BPFI  = {ff.BPFI:.2f} Hz")
    print(f"    2*BSF = {ff.two_BSF:.2f} Hz")

    # 데이터 로드
    print("\n[1/3] Loading .mat files ...")
    signals = load_all_signals(args.data_dir)
    print(f"  Loaded {len(signals)} files.")

    # 특징 추출
    print("\n[2/3] Extracting features ...")
    X, y = build_dataset(signals, rpm=args.rpm)

    # 학습 + 평가 + 저장
    print("\n[3/3] Training and evaluating ...")
    model, metrics = train_and_evaluate(X, y)
    save_model(model, metrics, args.output, rpm=args.rpm)

    print("\n  Done.")


if __name__ == "__main__":
    main()
