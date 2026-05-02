from collections import Counter, defaultdict
from pathlib import Path
import math

import matplotlib.pyplot as plt
import numpy as np

from corpus_data import split_corpus, vocabulary

FIG_DIR = Path(__file__).resolve().parent.parent / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def build_counts(corpus: list[list[str]], n: int) -> tuple[Counter, Counter]:
    ng: Counter = Counter()
    hg: Counter = Counter()
    for s in corpus:
        padded = ["<s>"] * (n - 2) + s if n >= 2 else s
        if len(padded) < n:
            continue
        for i in range(len(padded) - n + 1):
            tup = tuple(padded[i : i + n])
            ng[tup] += 1
            if n >= 2:
                hg[tup[:-1]] += 1
    if n == 1:
        hg[()] = sum(ng.values())
    return ng, hg


def mle_prob(
    history: tuple, word: str, ng: Counter, hg: Counter, n: int
) -> float:
    if n == 1:
        return ng.get((word,), 0) / hg[()]
    return ng.get(history + (word,), 0) / hg.get(history, 0) if hg.get(history, 0) > 0 else 0.0


def perplexity(
    test: list[list[str]],
    ng: Counter,
    hg: Counter,
    n: int,
    *,
    backoff_unigram: tuple[Counter, Counter] | None = None,
    eps: float = 1e-12,
) -> tuple[float, dict]:
    log_sum = 0.0
    n_tokens = 0
    n_zero = 0
    n_total = 0

    uni_ng = uni_hg = None
    if backoff_unigram is not None:
        uni_ng, uni_hg = backoff_unigram

    for s in test:
        padded = ["<s>"] * (n - 2) + s if n >= 2 else s
        if len(padded) < n:
            continue
        for i in range(n - 1, len(padded)):
            history = tuple(padded[i - (n - 1) : i]) if n >= 2 else ()
            w = padded[i]
            p = mle_prob(history, w, ng, hg, n)
            n_total += 1
            if p == 0:
                n_zero += 1
                if backoff_unigram is None:
                    return math.inf, dict[str, int](zero=n_zero, total=n_total)
                p = uni_ng.get((w,), 0) / uni_hg[()]
                if p == 0:
                    p = eps
            log_sum += math.log(p)
            n_tokens += 1

    if n_tokens == 0:
        return math.inf, dict(zero=n_zero, total=n_total)
    avg_neg_log = -log_sum / n_tokens
    return math.exp(avg_neg_log), dict(zero=n_zero, total=n_total)


def perplexity_vs_n(
    n_runs: int = 20, max_n: int = 4
) -> dict[str, np.ndarray]:
    train_ppls = np.zeros((max_n, n_runs))
    test_ppls_raw = np.full((max_n, n_runs), np.nan)
    test_ppls_bo = np.zeros((max_n, n_runs))
    zero_ratio = np.zeros((max_n, n_runs))

    for r in range(n_runs):
        train, test = split_corpus(seed=r, train_ratio=0.8)
        uni_ng, uni_hg = build_counts(train, 1)

        for ni, n in enumerate(range(1, max_n + 1)):
            ng, hg = build_counts(train, n)
            ppl_train, _ = perplexity(train, ng, hg, n,
                                      backoff_unigram=(uni_ng, uni_hg))
            ppl_raw, info = perplexity(test, ng, hg, n)
            ppl_bo, _ = perplexity(test, ng, hg, n,
                                   backoff_unigram=(uni_ng, uni_hg))
            train_ppls[ni, r] = ppl_train
            if math.isfinite(ppl_raw):
                test_ppls_raw[ni, r] = ppl_raw
            test_ppls_bo[ni, r] = ppl_bo
            zero_ratio[ni, r] = info["zero"] / max(info["total"], 1)

    return dict(
        train=train_ppls,
        test_raw=test_ppls_raw,
        test_bo=test_ppls_bo,
        zero_ratio=zero_ratio,
    )


def plot_perplexity(results: dict, max_n: int = 4) -> Path:
    ns = np.arange(1, max_n + 1)
    train_mean = results["train"].mean(axis=1)
    train_std = results["train"].std(axis=1)
    test_bo_mean = results["test_bo"].mean(axis=1)
    test_bo_std = results["test_bo"].std(axis=1)
    zero_mean = results["zero_ratio"].mean(axis=1) * 100

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    ax = axes[0]
    ax.plot(ns, train_mean, "o-", linewidth=2, label="train ppl", color="C0")
    ax.fill_between(ns, train_mean - train_std, train_mean + train_std,
                    alpha=0.2, color="C0")
    ax.plot(ns, test_bo_mean, "s-", linewidth=2,
            label="test ppl (with unigram backoff)", color="C3")
    ax.fill_between(ns, test_bo_mean - test_bo_std,
                    test_bo_mean + test_bo_std, alpha=0.2, color="C3")
    ax.set_yscale("log")
    ax.set_xticks(ns)
    ax.set_xlabel("n")
    ax.set_ylabel("perplexity (log scale)")
    ax.set_title("Perplexity drops with n on train,\n"
                 "but generalization gap widens on test")
    ax.legend()
    ax.grid(alpha=0.3, which="both")

    ax = axes[1]
    ax.plot(ns, zero_mean, "o-", linewidth=2, color="C3")
    ax.set_xticks(ns)
    ax.set_xlabel("n")
    ax.set_ylabel("% of test tokens with zero MLE prob")
    ax.set_title("Why unsmoothed test ppl = ∞:\nunseen n-grams pile up with n")
    ax.grid(alpha=0.3)

    fig.suptitle(
        f"Perplexity & sparsity vs n  ({results['train'].shape[1]} train/test splits)",
        fontsize=13, fontweight="bold")
    fig.tight_layout()
    out = FIG_DIR / "03_perplexity_vs_n.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"[saved] {out}")
    return out


if __name__ == "__main__":
    print("=== 03. Perplexity ===")
    train, test = split_corpus(seed=0, train_ratio=0.8)
    print(f"\nSplit (seed=0): train={len(train)} sents, test={len(test)} sents")
    print(f"Vocab on train: {len(vocabulary(train))}")

    print("\n[Single split: ppl by n]")
    print(f"  {'n':>3} {'ppl(train)':>12} {'ppl(test) raw':>15} "
          f"{'ppl(test) backoff':>18} {'zero %':>10}")
    uni_ng, uni_hg = build_counts(train, 1)
    for n in range(1, 5):
        ng, hg = build_counts(train, n)
        ppl_train, _ = perplexity(train, ng, hg, n,
                                  backoff_unigram=(uni_ng, uni_hg))
        ppl_raw, info = perplexity(test, ng, hg, n)
        ppl_bo, _ = perplexity(test, ng, hg, n,
                               backoff_unigram=(uni_ng, uni_hg))
        zero_pct = info["zero"] / max(info["total"], 1) * 100
        raw_str = "inf" if math.isinf(ppl_raw) else f"{ppl_raw:.1f}"
        print(f"  {n:>3} {ppl_train:>12.1f} {raw_str:>15} "
              f"{ppl_bo:>18.1f} {zero_pct:>9.1f}%")

    print("  -> train ppl 단조 감소, raw test ppl은 inf")
    print("  -> 단순 unigram backoff 만 붙여도 test ppl 이 유한, 그러나 여전히 큼")

    print("\n[Multi-split experiment (n_runs=20)]")
    results = perplexity_vs_n(n_runs=20, max_n=4)
    print(f"  {'n':>3} {'train ppl':>14} {'test ppl(bo)':>16} {'zero %':>10}")
    for ni in range(4):
        n = ni + 1
        tm = results["train"][ni].mean()
        ts = results["train"][ni].std()
        bm = results["test_bo"][ni].mean()
        bs = results["test_bo"][ni].std()
        zm = results["zero_ratio"][ni].mean() * 100
        print(f"  {n:>3} {tm:>8.1f}±{ts:>4.1f}  {bm:>9.1f}±{bs:>4.1f}  {zm:>9.1f}%")
    print("  -> WSJ 결과(uni 962 -> bi 170 -> tri 109) 와 동일한 단조감소 패턴")

    plot_perplexity(results, max_n=4)
