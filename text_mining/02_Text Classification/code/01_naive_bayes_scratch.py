
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

FIG_DIR = Path(__file__).resolve().parent.parent / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


class MultinomialNBScratch:
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self.classes_ = None
        self.vocab_ = None
        self.log_prior_ = None        # shape (C,)
        self.log_cond_ = None         # shape (C, |V|)
        self.class_word_counts_ = None  # shape (C, |V|)
        self.class_total_ = None      # shape (C,)

    def fit(self, docs, labels):
        tokenized = [d.split() for d in docs]
        vocab = sorted({w for doc in tokenized for w in doc})
        self.vocab_ = vocab
        word_to_idx = {w: i for i, w in enumerate(vocab)}

        classes = sorted(set(labels))
        self.classes_ = classes
        V = len(vocab)
        C = len(classes)

        # P(c) = N_c / N
        n = len(docs)
        class_counts = Counter(labels)
        self.log_prior_ = np.array(
            [np.log(class_counts[c] / n) for c in classes]
        )

        # Count(w, c)
        cw = np.zeros((C, V), dtype=float)
        for doc, y in zip(tokenized, labels):
            ci = classes.index(y)
            for w in doc:
                cw[ci, word_to_idx[w]] += 1
        self.class_word_counts_ = cw
        self.class_total_ = cw.sum(axis=1)

        # Laplace smoothing: (count + alpha) / (sum + alpha*|V|)
        self.log_cond_ = np.log(
            (cw + self.alpha) /
            (self.class_total_[:, None] + self.alpha * V)
        )
        return self

    def _doc_to_indices(self, doc, drop_unk=True):
        w2i = {w: i for i, w in enumerate(self.vocab_)}
        out = []
        for w in doc.split():
            if w in w2i:
                out.append(w2i[w])
            elif not drop_unk:
                out.append(None)
        return out

    def predict_log_proba(self, docs):
        out = np.zeros((len(docs), len(self.classes_)))
        for i, d in enumerate(docs):
            idxs = self._doc_to_indices(d)
            out[i] = self.log_prior_ + self.log_cond_[:, idxs].sum(axis=1)
        return out

    def predict(self, docs):
        logp = self.predict_log_proba(docs)
        return np.array(
            [self.classes_[i] for i in logp.argmax(axis=1)]
        )


STOPWORDS = {"with"}


def preprocess(text):
    toks = text.lower().split()
    return " ".join(t for t in toks if t not in STOPWORDS)


def naive_bayes_example():
    train_docs_raw = [
        "just plain boring",
        "entirely predictable and lacks energy",
        "no surprises and very few laughs",
        "very powerful",
        "the most fun film of the summer",
    ]
    train_labels = ["-", "-", "-", "+", "+"]
    test_doc_raw = "predictable with no fun"

    train_docs = [preprocess(t) for t in train_docs_raw]
    test_doc = preprocess(test_doc_raw)

    clf = MultinomialNBScratch(alpha=1.0).fit(train_docs, train_labels)

    V = len(clf.vocab_)
    total_neg = clf.class_total_[clf.classes_.index("-")]
    total_pos = clf.class_total_[clf.classes_.index("+")]

    print("=" * 60)
    print("Naive Bayes example")
    print("=" * 60)
    print(f"Vocabulary size |V| = {V}")
    print(f"Total word count in (-) class: {int(total_neg)}")
    print(f"Total word count in (+) class: {int(total_pos)}")

    print(f"\nPriors (from training):")
    for c, lp in zip(clf.classes_, clf.log_prior_):
        print(f"  P({c}) = {np.exp(lp):.4f}  (= N_c / N)")

    for w in ["predictable", "no", "fun"]:
        for c in ["-", "+"]:
            ci = clf.classes_.index(c)
            wi = clf.vocab_.index(w) if w in clf.vocab_ else None
            raw = clf.class_word_counts_[ci, wi] if wi is not None else 0
            denom = clf.class_total_[ci] + V
            print(
                f"  P('{w}'|{c}) = ({int(raw)}+1)/({int(clf.class_total_[ci])}"
                f"+{V}) = {(raw + 1) / denom:.5f}"
            )

    logp = clf.predict_log_proba([test_doc])[0]
    pred = clf.predict([test_doc])[0]
    print(f"\nTest document: '{test_doc}'")
    for c, lp in zip(clf.classes_, logp):
        print(f"  log P({c}) + Σ log P(w|{c}) = {lp:.4f}  "
              f"-> P => exp = {np.exp(lp):.3e}")
    print(f"  -> prediction = {pred}")

    return clf, test_doc, logp


def plot_token_contribution(clf, test_doc, logp):
    toks = [t for t in test_doc.split() if t in clf.vocab_]
    w2i = {w: i for i, w in enumerate(clf.vocab_)}

    contribs = np.zeros((len(toks), len(clf.classes_)))
    for i, t in enumerate(toks):
        contribs[i] = clf.log_cond_[:, w2i[t]]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    ax = axes[0]
    x = np.arange(len(toks))
    width = 0.35
    ax.bar(x - width / 2, contribs[:, 0], width,
           label=f"class = {clf.classes_[0]}", color="C3")
    ax.bar(x + width / 2, contribs[:, 1], width,
           label=f"class = {clf.classes_[1]}", color="C0")
    ax.set_xticks(x)
    ax.set_xticklabels(toks)
    ax.set_ylabel(r"$\log P(w|c)$")
    ax.set_title("Per-token log likelihood (higher = better fit)")
    ax.legend()
    ax.grid(alpha=0.3)

    ax = axes[1]
    cum_neg = [clf.log_prior_[0]] + list(
        clf.log_prior_[0] + np.cumsum(contribs[:, 0])
    )
    cum_pos = [clf.log_prior_[1]] + list(
        clf.log_prior_[1] + np.cumsum(contribs[:, 1])
    )
    xs = ["prior"] + toks
    ax.plot(xs, cum_neg, "o-", linewidth=2, color="C3",
            label=f"class = {clf.classes_[0]}")
    ax.plot(xs, cum_pos, "s-", linewidth=2, color="C0",
            label=f"class = {clf.classes_[1]}")
    ax.set_ylabel(r"$\log P(c) + \sum \log P(w|c)$")
    ax.set_title("Cumulative log score as each token is consumed")
    ax.legend()
    ax.grid(alpha=0.3)

    fig.suptitle(
        f"Naive Bayes on example: test = 'predictable no fun'  "
        f"-> predicted class = '{clf.classes_[int(np.argmax(logp))]}'",
        fontsize=12,
    )
    fig.tight_layout()
    out = FIG_DIR / "01_naive_bayes_example.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"\n[saved] {out}")


# 검증용
def synthetic_sanity_check():
    rng = np.random.default_rng(42)

    pos_words = ["great", "fun", "powerful", "excellent", "enjoy",
                 "love", "wonderful", "best"]
    neg_words = ["boring", "terrible", "awful", "dull", "bad",
                 "worst", "predictable", "waste"]
    neutral = ["movie", "film", "the", "a", "and", "i", "it", "was"]

    def sample_doc(label, rng):
        length = rng.integers(6, 12)
        topic = pos_words if label == "+" else neg_words
        mix = rng.choice(topic, size=rng.integers(2, 4)).tolist() + \
              rng.choice(neutral, size=length - 2).tolist()
        rng.shuffle(mix)
        return " ".join(mix)

    n_train, n_test = 200, 100
    train_labels = rng.choice(["+", "-"], size=n_train).tolist()
    train_docs = [sample_doc(y, rng) for y in train_labels]
    test_labels = rng.choice(["+", "-"], size=n_test).tolist()
    test_docs = [sample_doc(y, rng) for y in test_labels]

    clf = MultinomialNBScratch(alpha=1.0).fit(train_docs, train_labels)
    preds = clf.predict(test_docs)
    acc = np.mean(np.array(preds) == np.array(test_labels))
    print(f"\n[sanity check] synthetic corpus  "
          f"train={n_train}, test={n_test}  -> accuracy = {acc:.3f}")
    return acc


if __name__ == "__main__":
    print("=== 01. Naïve Bayes from scratch ===\n")
    clf, test_doc, logp = naive_bayes_example()
    plot_token_contribution(clf, test_doc, logp)
    synthetic_sanity_check()
