from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.feature_extraction.text import (CountVectorizer,
                                             TfidfVectorizer)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

FIG_DIR = Path(__file__).resolve().parent.parent / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


POS = ["great", "fun", "powerful", "excellent", "enjoyable",
       "brilliant", "wonderful", "amazing", "thrilling"]
NEG = ["boring", "terrible", "awful", "dull", "predictable",
       "tedious", "disappointing", "shallow", "painful"]

STOP_LIKE = ["the", "is", "on", "of", "and", "a", "to", "this", "that",
             "in", "for", "with", "at", "by", "an"]
COMMON = ["movie", "film", "was", "i", "it", "really", "quite"]


N_TOPIC = (1, 3)
N_COMMON = (2, 5)
N_STOP = (40, 60)


def sample_doc(label, rng):
    topic = POS if label == "+" else NEG
    words = (
        rng.choice(topic, size=rng.integers(*N_TOPIC)).tolist()
        + rng.choice(COMMON, size=rng.integers(*N_COMMON)).tolist()
        + rng.choice(STOP_LIKE, size=rng.integers(*N_STOP)).tolist()
    )
    rng.shuffle(words)
    return " ".join(words)


def make_corpus(n_docs, rng):
    labels = rng.choice(["+", "-"], size=n_docs).tolist()
    docs = [sample_doc(y, rng) for y in labels]
    return docs, labels


def run_experiment(n_runs=30, n_docs=60):
    rows = []  # (repr, model, acc)
    for r in range(n_runs):
        rng = np.random.default_rng(2000 + r)
        docs, labels = make_corpus(n_docs, rng)
        X_tr_raw, X_te_raw, y_tr, y_te = train_test_split(
            docs, labels, test_size=0.5, random_state=r, stratify=labels,
        )

        for repr_name, Vec in [("BoW", CountVectorizer),
                               ("TF-IDF", TfidfVectorizer)]:
            vec = Vec()
            Xtr = vec.fit_transform(X_tr_raw)
            Xte = vec.transform(X_te_raw)

            for model_name, Model, kw in [
                ("NB", MultinomialNB, dict(alpha=1.0)),
                # LR: 정규화를 약하게 (C=10) 해서 stop-like 영향이 그대로 드러나게
                ("LR", LogisticRegression, dict(max_iter=2000, C=10.0)),
            ]:
                clf = Model(**kw).fit(Xtr, y_tr)
                pred = clf.predict(Xte)
                rows.append((repr_name, model_name,
                             accuracy_score(y_te, pred)))
    return rows


def summarize(rows):
    from collections import defaultdict
    agg = defaultdict(list)
    for repr_name, model, acc in rows:
        agg[(repr_name, model)].append(acc)
    summary = {}
    for k, accs in agg.items():
        summary[k] = (np.mean(accs), np.std(accs))
    return summary


def compute_idf_spectrum(seed=0, n_docs=200):
    rng = np.random.default_rng(seed)
    docs, _ = make_corpus(n_docs, rng)
    vec = TfidfVectorizer()
    vec.fit(docs)

    words = vec.get_feature_names_out()
    idfs = vec.idf_

    def group_of(w):
        if w in STOP_LIKE:
            return "stop-like"
        if w in COMMON:
            return "common"
        if w in POS:
            return "positive"
        if w in NEG:
            return "negative"
        return "other"

    groups = np.array([group_of(w) for w in words])
    return words, idfs, groups


def plot(rows, summary):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ax = axes[0]
    words, idfs, groups = compute_idf_spectrum()
    order = np.argsort(idfs)
    words, idfs, groups = words[order], idfs[order], groups[order]

    color_map = {"stop-like": "gray", "common": "C0",
                 "positive": "C2", "negative": "C3", "other": "lightgray"}
    xs = np.arange(len(words))
    for g in ["stop-like", "common", "positive", "negative", "other"]:
        mask = groups == g
        if mask.any():
            ax.bar(xs[mask], idfs[mask], color=color_map[g], label=g)

    ax.set_xticks(xs)
    ax.set_xticklabels(words, rotation=80, fontsize=7)
    ax.set_ylabel(r"IDF weight  ($\log\,(1+N)/(1+df)\,+\,1$)")
    ax.set_title("IDF spectrum: stop-like words get the lowest weights")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(alpha=0.3, axis="y")

    ax = axes[1]
    labels_order = [("BoW", "NB"), ("TF-IDF", "NB"),
                    ("BoW", "LR"), ("TF-IDF", "LR")]
    xticks = [f"{r}\n{m}" for r, m in labels_order]
    means = [summary[k][0] for k in labels_order]
    stds = [summary[k][1] for k in labels_order]

    colors = ["C0", "C2", "C0", "C2"]
    bars = ax.bar(np.arange(4), means, yerr=stds, capsize=6,
                  color=colors, edgecolor="black", linewidth=0.5)
    ax.set_xticks(np.arange(4))
    ax.set_xticklabels(xticks)
    ax.set_ylabel("Test accuracy (mean ± std, 20 repeats)")
    ax.set_title("TF-IDF (green) vs BoW (blue)")
    ax.set_ylim(0.5, 1.02)
    ax.grid(alpha=0.3, axis="y")

    for b, m, s in zip(bars, means, stds):
        ax.text(b.get_x() + b.get_width() / 2,
                m + s + 0.005, f"{m:.3f}",
                ha="center", fontsize=9)

    fig.suptitle("BoW vs TF-IDF: how much does down-weighting stop-words help?",
                 fontsize=12)
    fig.tight_layout()
    out = FIG_DIR / "03_tfidf_representation.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"[saved] {out}")


if __name__ == "__main__":
    print("=== 03. BoW vs TF-IDF representations ===")
    rows = run_experiment(n_runs=30, n_docs=60)
    summary = summarize(rows)

    print(f"\n{'repr':>8}  {'model':>5}  {'acc mean':>9}  {'std':>6}")
    for (repr_name, model), (m, s) in sorted(summary.items()):
        print(f"  {repr_name:>6}  {model:>5}  {m:>9.4f}  {s:>6.4f}")

    bow_lr = summary[("BoW", "LR")][0]
    tfidf_lr = summary[("TF-IDF", "LR")][0]
    print(f"\n  -> LR: BoW {bow_lr:.3f}  vs  TF-IDF {tfidf_lr:.3f}  "
          f"(gain = {tfidf_lr - bow_lr:+.3f})")
    bow_nb = summary[("BoW", "NB")][0]
    tfidf_nb = summary[("TF-IDF", "NB")][0]
    print(f"  -> NB: BoW {bow_nb:.3f}  vs  TF-IDF {tfidf_nb:.3f}  "
          f"(gain = {tfidf_nb - bow_nb:+.3f})")

    plot(rows, summary)
