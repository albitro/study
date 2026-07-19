from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from corpus_data import get_corpus

FIG_DIR = Path(__file__).resolve().parent.parent / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def build_ngram(corpus: list[list[str]], n: int) -> dict:
    if n == 1:
        c: Counter = Counter()
        for s in corpus:
            for w in s:
                c[w] += 1
        total = sum(c.values())
        return {(): {w: cnt / total for w, cnt in c.items()}}

    n_counts: Counter = Counter()
    for s in corpus:
        padded = ["<s>"] * (n - 2) + s
        if len(padded) < n:
            continue
        for i in range(len(padded) - n + 1):
            n_counts[tuple(padded[i : i + n])] += 1

    h_counts: Counter = Counter()
    for ng, cnt in n_counts.items():
        h_counts[ng[:-1]] += cnt

    table: dict = defaultdict(dict)
    for ng, cnt in n_counts.items():
        h, w = ng[:-1], ng[-1]
        table[h][w] = cnt / h_counts[h]
    return table


def _sample(words: list[str], probs: np.ndarray, rng: np.random.Generator) -> str:
    probs = probs / probs.sum()
    idx = rng.choice(len(words), p=probs)
    return words[idx]


def decode_greedy(dist: dict[str, float]) -> str:
    return max(dist.items(), key=lambda x: x[1])[0]


def decode_topk(dist: dict[str, float], k: int, rng: np.random.Generator) -> str:
    items = sorted(dist.items(), key=lambda x: -x[1])[:k]
    words, probs = zip(*items)
    return _sample(list(words), np.array(probs), rng)


def decode_topp(dist: dict[str, float], p: float, rng: np.random.Generator) -> str:
    items = sorted(dist.items(), key=lambda x: -x[1])
    cum, kept = 0.0, []
    for w, prob in items:
        kept.append((w, prob))
        cum += prob
        if cum >= p:
            break
    words, probs = zip(*kept)
    return _sample(list(words), np.array(probs), rng)


def decode_full_sample(dist: dict[str, float], rng: np.random.Generator) -> str:
    words = list(dist.keys())
    probs = np.array(list(dist.values()))
    return _sample(words, probs, rng)


def generate_sentence(
    table: dict,
    n: int,
    decoder: str = "sample",
    k: int = 5,
    p: float = 0.9,
    max_len: int = 25,
    seed: int = 0,
) -> list[str]:
    rng = np.random.default_rng(seed)
    if n == 1:
        out = []
        for _ in range(max_len):
            dist = table[()]
            w = _pick(dist, decoder, k, p, rng)
            if w == "</s>":
                break
            if w == "<s>":
                continue
            out.append(w)
        return out

    out = ["<s>"] * (n - 1)
    for _ in range(max_len):
        history = tuple(out[-(n - 1):])
        if history not in table:
            break
        dist = table[history]
        w = _pick(dist, decoder, k, p, rng)
        out.append(w)
        if w == "</s>":
            break
    return [w for w in out if w not in ("<s>", "</s>")]


def _pick(dist, decoder, k, p, rng):
    if decoder == "greedy":
        return decode_greedy(dist)
    if decoder == "topk":
        return decode_topk(dist, k, rng)
    if decoder == "topp":
        return decode_topp(dist, p, rng)
    if decoder == "sample":
        return decode_full_sample(dist, rng)
    raise ValueError(decoder)


def plot_decoding_methods() -> Path:
    tokens = ["for", "to", "with", "and", "by"]
    probs = np.array([0.40, 0.25, 0.17, 0.13, 0.05])

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharey=True)

    # Greedy
    ax = axes[0]
    colors = ["C3" if i == 0 else "lightgray" for i in range(len(tokens))]
    ax.bar(tokens, probs, color=colors, edgecolor="black")
    ax.set_title("Greedy → only 'for'")
    ax.set_ylabel("probability")
    ax.grid(alpha=0.3, axis="y")

    # Top-k k=3
    ax = axes[1]
    colors = ["C0" if i < 3 else "lightgray" for i in range(len(tokens))]
    ax.bar(tokens, probs, color=colors, edgecolor="black")
    ax.set_title("Top-k (k=3) → {for, to, with}")
    ax.grid(alpha=0.3, axis="y")

    # Top-p p=0.6
    ax = axes[2]
    cum = np.cumsum(probs)
    last = int(np.argmax(cum >= 0.6))  # 0.40+0.25 = 0.65 >= 0.6
    colors = ["C2" if i <= last else "lightgray" for i in range(len(tokens))]
    ax.bar(tokens, probs, color=colors, edgecolor="black")
    ax.set_title("Top-p (p=0.6) → {for, to}")
    ax.grid(alpha=0.3, axis="y")

    fig.suptitle('Decoding methods on "is helpful ___"',
                 fontsize=13, fontweight="bold")
    fig.tight_layout()
    out = FIG_DIR / "02_decoding_methods.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"[saved] {out}")
    return out


def diversity_experiment(
    table: dict, n: int, n_runs: int = 100
) -> dict[str, float]:
    settings = {
        "greedy": dict(decoder="greedy"),
        "top-k=3": dict(decoder="topk", k=3),
        "top-k=10": dict(decoder="topk", k=10),
        "top-p=0.6": dict(decoder="topp", p=0.6),
        "top-p=0.9": dict(decoder="topp", p=0.9),
        "full sample": dict(decoder="sample"),
    }
    out = {}
    for name, kw in settings.items():
        all_tokens = []
        for r in range(n_runs):
            sent = generate_sentence(table, n, seed=1000 + r, **kw)
            all_tokens.extend(sent)
        if not all_tokens:
            out[name] = 0.0
        else:
            out[name] = len(set(all_tokens)) / len(all_tokens)
    return out


def plot_diversity(div_bi: dict, div_tri: dict) -> Path:
    names = list(div_bi.keys())
    bi = [div_bi[n] for n in names]
    tri = [div_tri[n] for n in names]

    x = np.arange(len(names))
    w = 0.35
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(x - w / 2, bi, w, label="bigram", color="C0", edgecolor="black")
    ax.bar(x + w / 2, tri, w, label="trigram", color="C1", edgecolor="black")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=20)
    ax.set_ylabel("type / token ratio across 100 generations")
    ax.set_title("Decoding method controls output diversity")
    ax.legend()
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    out = FIG_DIR / "02_diversity.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"[saved] {out}")
    return out


if __name__ == "__main__":
    print("=== 02. Generation methods ===")
    corpus = get_corpus()
    print(f"\nCorpus: {len(corpus)} sentences")

    uni = build_ngram(corpus, 1)
    bi = build_ngram(corpus, 2)
    tri = build_ngram(corpus, 3)

    print("\n[Sentence samples by n-gram order]")
    for n, table, name in [(1, uni, "unigram"), (2, bi, "bigram"), (3, tri, "trigram")]:
        print(f"\n  -- {name} (full sampling) --")
        for s in range(5):
            sent = generate_sentence(table, n, decoder="sample", seed=s, max_len=15)
            print(f"   [{s}] {' '.join(sent)}")

    print("\n  -> unigram 은 단순 단어 나열, bigram 부터 인접 단어 응집, trigram 은 학습 문장에 가까워짐")

    print("\n[Same trigram model, different decoders]")
    for dec in ["greedy", "topk", "topp", "sample"]:
        print(f"\n  -- decoder = {dec} --")
        for s in range(3):
            kw = {}
            if dec == "topk":
                kw = dict(k=3)
            elif dec == "topp":
                kw = dict(p=0.6)
            sent = generate_sentence(tri, 3, decoder=dec, seed=s, max_len=15, **kw)
            print(f"   [{s}] {' '.join(sent)}")

    print("\n[Diversity experiment: type/token ratio over 100 sentences]")
    div_bi = diversity_experiment(bi, 2, n_runs=100)
    div_tri = diversity_experiment(tri, 3, n_runs=100)
    print(f"  {'method':<14} {'bigram':>10} {'trigram':>10}")
    for k in div_bi:
        print(f"  {k:<14} {div_bi[k]:>10.3f} {div_tri[k]:>10.3f}")
    print("  -> greedy 는 거의 같은 토큰만 반복, top-p 와 top-k 가 균형 잡힌 다양성")

    plot_decoding_methods()
    plot_diversity(div_bi, div_tri)
