from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from corpus_data import get_corpus, vocabulary

FIG_DIR = Path(__file__).resolve().parent.parent / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def count_ngrams(corpus: list[list[str]], n: int) -> Counter:
    c: Counter = Counter()
    for sent in corpus:
        if len(sent) < n:
            continue
        for i in range(len(sent) - n + 1):
            c[tuple(sent[i : i + n])] += 1
    return c


def conditional_prob_table(corpus: list[list[str]], n: int) -> dict:
    if n < 2:
        raise ValueError("use unigram_prob for n=1")
    n_counts = count_ngrams(corpus, n)
    h_counts: Counter = Counter()
    for ng, cnt in n_counts.items():
        h_counts[ng[:-1]] += cnt
    table: dict = defaultdict(dict)
    for ng, cnt in n_counts.items():
        history, w = ng[:-1], ng[-1]
        table[history][w] = cnt / h_counts[history]
    return table


def unigram_prob(corpus: list[list[str]]) -> dict:
    c = count_ngrams(corpus, 1)
    total = sum(c.values())
    return {w[0]: cnt / total for w, cnt in c.items()}


def gram_probs(corpus: list[list[str]]) -> None:
    print("\n 조건부 확률 (MLE) 몇 개 출력")
    bigram = conditional_prob_table(corpus, 2)
    trigram = conditional_prob_table(corpus, 3)

    examples_bi = [("the",), ("a",), ("i",)]
    print("\n  -- bigram P(w | history) top-5 --")
    for h in examples_bi:
        if h not in bigram:
            continue
        top = sorted(bigram[h].items(), key=lambda x: -x[1])[:5]
        pretty = ", ".join(f"{w}:{p:.3f}" for w, p in top)
        print(f"  P(w | {h[0]}) = [{pretty}]")

    examples_tri = [("the", "cat"), ("the", "dog"), ("i", "like")]
    print("\n  -- trigram P(w | history) top-5 --")
    for h in examples_tri:
        if h not in trigram:
            continue
        top = sorted(trigram[h].items(), key=lambda x: -x[1])[:5]
        pretty = ", ".join(f"{w}:{p:.3f}" for w, p in top)
        print(f"  P(w | {' '.join(h)}) = [{pretty}]")


def sparsity_table(
    corpus: list[list[str]], vocab_size: int, max_n: int = 5
) -> list[dict]:
    rows = []
    for n in range(1, max_n + 1):
        c = count_ngrams(corpus, n)
        n_unique = len(c)
        possible = vocab_size**n
        rows.append(
            dict(
                n=n,
                possible=possible,
                observed=n_unique,
                ratio=n_unique / possible,
            )
        )
    return rows


def plot_sparsity(rows: list[dict]) -> Path:
    ns = [r["n"] for r in rows]
    possible = [r["possible"] for r in rows]
    observed = [r["observed"] for r in rows]
    ratios = [r["ratio"] for r in rows]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    ax = axes[0]
    ax.plot(ns, possible, "s--", linewidth=2, label=r"possible $V^n$", color="C3")
    ax.plot(ns, observed, "o-", linewidth=2, label="observed in corpus", color="C0")
    ax.set_yscale("log")
    ax.set_xlabel("n")
    ax.set_ylabel("count (log scale)")
    ax.set_title("n-gram space explodes as $V^n$")
    ax.set_xticks(ns)
    ax.legend()
    ax.grid(alpha=0.3, which="both")

    ax = axes[1]
    ax.plot(ns, ratios, "o-", linewidth=2, color="C0")
    ax.set_yscale("log")
    ax.set_xlabel("n")
    ax.set_ylabel("observed / possible (log scale)")
    ax.set_title("Fraction of n-grams ever seen → 0 very fast")
    ax.set_xticks(ns)
    ax.grid(alpha=0.3, which="both")

    fig.suptitle(
        "Why naive MLE breaks: n-gram sparsity",
        fontsize=13,
        fontweight="bold",
    )
    fig.tight_layout()
    out = FIG_DIR / "01_ngram_sparsity.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"[saved] {out}")
    return out


def plot_zipf(corpus: list[list[str]]) -> Path:
    c = count_ngrams(corpus, 1)
    counts = sorted([cnt for w, cnt in c.items() if w[0] not in ("<s>", "</s>")],
                    reverse=True)
    ranks = np.arange(1, len(counts) + 1)

    # 이론값 (1/rank * top)
    theory = counts[0] / ranks

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(ranks, counts, "o-", linewidth=2, label="observed (this corpus)", color="C0")
    ax.plot(ranks, theory, "--", linewidth=2,
            label=r"Zipf $\propto 1/\mathrm{rank}$", color="C3")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("rank (log)")
    ax.set_ylabel("frequency (log)")
    ax.set_title("Zipf's law on the toy corpus (log-log)")
    ax.grid(alpha=0.3, which="both")
    ax.legend()
    fig.tight_layout()
    out = FIG_DIR / "01_zipf.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"[saved] {out}")
    return out


if __name__ == "__main__":
    print("=== 01. n-gram basics ===")
    corpus = get_corpus()
    vocab = vocabulary(corpus)
    V = len(vocab)
    n_tokens = sum(len(s) for s in corpus)
    print(f"\nCorpus: {len(corpus)} sentences, {n_tokens} tokens, vocab size V={V}")

    gram_probs(corpus)

    print("\n[Sparsity] possible V^n vs observed unique n-grams")
    rows = sparsity_table(corpus, V, max_n=5)
    print(f"  {'n':>3} {'possible':>15} {'observed':>10} {'ratio':>14}")
    for r in rows:
        print(f"  {r['n']:>3} {r['possible']:>15,d} {r['observed']:>10,d} "
              f"{r['ratio']:>14.3e}")
    print("  -> 가능한 n-gram 중 실제 본 비율이 n=2 이후 1e-3 이하로 추락 -> 0 확률에 가까워짐")
    plot_sparsity(rows)
    plot_zipf(corpus)
