from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from importlib import import_module
nb_module = import_module("01_naive_bayes_scratch")
MultinomialNBScratch = nb_module.MultinomialNBScratch

FIG_DIR = Path(__file__).resolve().parent.parent / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


POS_WORDS = [
    "great", "fun", "powerful", "excellent", "enjoyable", "love",
    "wonderful", "best", "amazing", "brilliant", "delightful", "superb",
    "hilarious", "charming", "fantastic", "gorgeous", "thrilling",
    "touching", "heartwarming", "genius", "captivating", "lovely",
    "marvelous", "outstanding", "engaging", "refreshing", "remarkable",
    "uplifting", "witty", "stunning",
]
NEG_WORDS = [
    "boring", "terrible", "awful", "dull", "bad", "worst", "predictable",
    "waste", "lacks", "poor", "tedious", "mediocre", "forgettable",
    "cliched", "lame", "disappointing", "painful", "shallow", "bland",
    "annoying", "unbearable", "flat", "sloppy", "weak", "grating",
    "pointless", "stale", "unconvincing", "drab", "joyless",
]
NEUTRAL = [
    "movie", "film", "the", "a", "and", "i", "it", "was", "this", "that",
    "plot", "scene", "character", "director", "story", "cast", "actor",
    "script", "music", "camera", "opening", "ending", "dialogue",
    "moment", "line", "studio", "theater", "premiere", "trailer", "review",
]


def sample_doc(label, rng, n_topic=4, n_neutral=6, n_flip=0):
    topic = POS_WORDS if label == "+" else NEG_WORDS
    opposite = NEG_WORDS if label == "+" else POS_WORDS

    words = (
        rng.choice(topic, size=n_topic).tolist()
        + rng.choice(NEUTRAL, size=n_neutral).tolist()
        + rng.choice(opposite, size=n_flip).tolist()
    )
    rng.shuffle(words)
    return " ".join(words)


def make_corpus(n_docs, rng):
    labels = rng.choice(["+", "-"], size=n_docs).tolist()
    docs = [sample_doc(y, rng, n_topic=4, n_neutral=6, n_flip=1)
            for y in labels]
    return docs, labels


def run_one(alpha, seed, n_train=60, n_test=400):
    rng = np.random.default_rng(seed)
    train_docs, train_labels = make_corpus(n_train, rng)
    test_docs, test_labels = make_corpus(n_test, rng)

    if alpha == 0:
        return run_alpha_zero(train_docs, train_labels, test_docs, test_labels)

    clf = MultinomialNBScratch(alpha=alpha).fit(train_docs, train_labels)
    preds = clf.predict(test_docs)
    return np.mean(np.array(preds) == np.array(test_labels))


def run_alpha_zero(train_docs, train_labels, test_docs, test_labels):
    from collections import Counter
    classes = sorted(set(train_labels))
    tokenized = [d.split() for d in train_docs]
    vocab = sorted({w for doc in tokenized for w in doc})
    w2i = {w: i for i, w in enumerate(vocab)}
    C, V = len(classes), len(vocab)

    cw = np.zeros((C, V))
    for doc, y in zip(tokenized, train_labels):
        ci = classes.index(y)
        for w in doc:
            cw[ci, w2i[w]] += 1
    total = cw.sum(axis=1)
    cond = cw / total[:, None]

    n = len(train_docs)
    class_counts = Counter(train_labels)
    log_prior = np.array([np.log(class_counts[c] / n) for c in classes])

    preds = []
    for d in test_docs:
        scores = log_prior.copy()
        for w in d.split():
            if w in w2i:
                for ci in range(C):
                    p = cond[ci, w2i[w]]
                    if p == 0:
                        scores[ci] = -np.inf
                    else:
                        scores[ci] += np.log(p)
        if np.all(np.isneginf(scores)):
            preds.append(classes[int(np.argmax(log_prior))])
        else:
            preds.append(classes[int(np.argmax(scores))])
    return np.mean(np.array(preds) == np.array(test_labels))


def experiment(alphas, n_runs=20, n_train=60, n_test=400):
    results = np.zeros((len(alphas), n_runs))
    for i, a in enumerate(alphas):
        for r in range(n_runs):
            results[i, r] = run_one(a, seed=1000 + r,
                                     n_train=n_train, n_test=n_test)
    return results.mean(axis=1), results.std(axis=1)


def plot(alphas, mean, std):
    fig, ax = plt.subplots(figsize=(9, 5.5))

    xs_plot = [1e-4] + list(alphas[1:])
    ax.errorbar(xs_plot, mean, yerr=std, fmt="o-", linewidth=2,
                color="C0", markersize=7, capsize=4,
                label="Mean accuracy ± 1 std (20 repeats)")
    ax.fill_between(xs_plot, mean - std, mean + std,
                    alpha=0.2, color="C0")

    ax.scatter([1e-4], [mean[0]], s=200, facecolors="none",
               edgecolors="C3", linewidths=2, zorder=5)
    ax.annotate(r"$\alpha=0$: zero-prob collapse",
                xy=(1e-4, mean[0]), xytext=(3e-4, mean[0] + 0.04),
                color="C3", fontsize=10,
                arrowprops=dict(arrowstyle="->", color="C3"))

    best = int(np.argmax(mean))
    ax.annotate(rf"best $\alpha$ = {alphas[best]:g}"
                f"\nacc = {mean[best]:.3f}",
                xy=(xs_plot[best], mean[best]),
                xytext=(xs_plot[best] * 5, mean[best] - 0.05),
                fontsize=10, color="C2",
                arrowprops=dict(arrowstyle="->", color="C2"))

    ax.axhline(0.5, linestyle=":", color="gray",
               label="Random baseline (0.5)")
    ax.set_xscale("log")
    ax.set_xlabel(r"Laplace smoothing $\alpha$  "
                  r"(first point = $\alpha=0$)")
    ax.set_ylabel("Test accuracy")
    ax.set_title("Laplace smoothing: too small = zero-prob collapse, "
                 "too large = uniform-prior drift")
    ax.grid(alpha=0.3)
    ax.legend(loc="lower center")

    fig.tight_layout()
    out = FIG_DIR / "02_smoothing_effect.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"[saved] {out}")


if __name__ == "__main__":
    print("=== 02. Laplace smoothing effect ===")
    alphas = [0, 1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1000.0]
    mean, std = experiment(alphas, n_runs=20)

    print("\n[Smoothing summary]")
    print(f"  {'alpha':>10}  {'mean acc':>9}  {'std':>7}")
    for a, m, s in zip(alphas, mean, std):
        print(f"  {a:>10g}  {m:>9.4f}  {s:>7.4f}")

    best = int(np.argmax(mean))
    print(f"\n  → best α = {alphas[best]:g} (acc = {mean[best]:.3f})")
    print(f"  → α=0 acc = {mean[0]:.3f} (zero-prob collapse)")
    print(f"  → α=1000 acc = {mean[-1]:.3f} (over-smoothed)")

    plot(alphas, mean, std)
