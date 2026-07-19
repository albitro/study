from collections import Counter
from pathlib import Path
import math

import matplotlib.pyplot as plt
import numpy as np

from corpus_data import get_corpus, vocabulary

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


def laplace_bigram_prob(
    history: tuple, w: str, ng: Counter, hg: Counter, V: int, alpha: float
) -> float:
    num = ng.get(history + (w,), 0) + alpha
    den = hg.get(history, 0) + alpha * V
    return num / den


def abs_disc_bigram_prob(
    history: tuple,
    w: str,
    bi_ng: Counter,
    bi_hg: Counter,
    uni_ng: Counter,
    uni_total: int,
    seen_words: dict[tuple, set],
    d: float,
) -> float:
    cnt = bi_ng.get(history + (w,), 0)
    h_cnt = bi_hg.get(history, 0)
    if h_cnt == 0:
        return uni_ng.get((w,), 0) / uni_total if uni_total > 0 else 0.0
    if cnt > 0:
        return max(cnt - d, 0) / h_cnt
    n_seen = len(seen_words.get(history, set()))
    alpha_h = d * n_seen / h_cnt
    p_uni = uni_ng.get((w,), 0) / uni_total if uni_total > 0 else 0.0
    return alpha_h * p_uni


def interp_prob(
    h2: tuple,
    w: str,
    tri_ng: Counter,
    tri_hg: Counter,
    bi_ng: Counter,
    bi_hg: Counter,
    uni_ng: Counter,
    uni_total: int,
    lambdas: tuple[float, float, float],
) -> float:
    l1, l2, l3 = lambdas

    h_cnt = tri_hg.get(h2, 0)
    p_tri = tri_ng.get(h2 + (w,), 0) / h_cnt if h_cnt > 0 else 0.0

    h1 = (h2[-1],) if len(h2) > 0 else ()
    h_cnt_b = bi_hg.get(h1, 0)
    p_bi = bi_ng.get(h1 + (w,), 0) / h_cnt_b if h_cnt_b > 0 else 0.0

    p_uni = uni_ng.get((w,), 0) / uni_total if uni_total > 0 else 0.0
    return l1 * p_tri + l2 * p_bi + l3 * p_uni


def perplexity_of(
    test: list[list[str]], n_context: int, prob_fn, eps: float = 1e-12
) -> float:
    log_sum = 0.0
    n_tok = 0
    for s in test:
        padded = ["<s>"] * n_context + s if n_context >= 1 else s
        for i in range(n_context, len(padded)):
            history = tuple(padded[i - n_context : i])
            w = padded[i]
            p = prob_fn(history, w)
            if p <= 0:
                if eps <= 0:
                    return math.inf
                p = eps
            log_sum += math.log(p)
            n_tok += 1
    if n_tok == 0:
        return math.inf
    return math.exp(-log_sum / n_tok)


def evaluate_one_split(
    train: list[list[str]],
    dev: list[list[str]],
    test: list[list[str]],
    alphas: np.ndarray,
    discounts: np.ndarray,
    lambdas_grid: list[tuple[float, float, float]],
) -> dict:
    V = len(vocabulary(train + [["<s>"], ["</s>"]]))
    bi_ng, bi_hg = build_counts(train, 2)
    tri_ng, tri_hg = build_counts(train, 3)
    uni_ng, _ = build_counts(train, 1)
    uni_total = sum(uni_ng.values())

    seen_words: dict[tuple, set] = {}
    for ng_ in bi_ng:
        seen_words.setdefault(ng_[:-1], set()).add(ng_[-1])

    def p_un(h, w):
        d_ = bi_hg.get(h, 0)
        return bi_ng.get(h + (w,), 0) / d_ if d_ > 0 else 0.0
    ppl_un = perplexity_of(test, 1, p_un, eps=0.0)

    ppl_laplace = []
    for a in alphas:
        ppl_laplace.append(perplexity_of(
            test, 1, lambda h, w, a=a: laplace_bigram_prob(h, w, bi_ng, bi_hg, V, a)
        ))

    ppl_disc = []
    for d in discounts:
        ppl_disc.append(perplexity_of(
            test, 1,
            lambda h, w, d=d: abs_disc_bigram_prob(
                h, w, bi_ng, bi_hg, uni_ng, uni_total, seen_words, d
            )
        ))

    best_dev_ppl = math.inf
    best_lams = None
    for lams in lambdas_grid:
        ppl_dev = perplexity_of(
            dev, 2,
            lambda h, w, lams=lams: interp_prob(
                h, w, tri_ng, tri_hg, bi_ng, bi_hg, uni_ng, uni_total, lams
            )
        )
        if ppl_dev < best_dev_ppl:
            best_dev_ppl = ppl_dev
            best_lams = lams
    ppl_interp_test = perplexity_of(
        test, 2,
        lambda h, w: interp_prob(
            h, w, tri_ng, tri_hg, bi_ng, bi_hg, uni_ng, uni_total, best_lams
        )
    )

    return dict(
        ppl_unsmoothed=ppl_un,
        ppl_laplace=np.array(ppl_laplace),
        ppl_disc=np.array(ppl_disc),
        ppl_interp=ppl_interp_test,
        best_lams=best_lams,
        best_dev_ppl=best_dev_ppl,
    )


def run(
    n_runs: int = 15
) -> dict:
    alphas = np.array([1e-4, 1e-3, 1e-2, 5e-2, 0.1, 0.3, 1.0, 3.0, 10.0])
    discounts = np.array([0.1, 0.25, 0.5, 0.75, 0.9])
    lambdas_grid = []
    step = 0.1
    for l1 in np.arange(0, 1.01, step):
        for l2 in np.arange(0, 1.01 - l1, step):
            l3 = 1 - l1 - l2
            if l3 < -1e-9:
                continue
            lambdas_grid.append((round(l1, 2), round(l2, 2), round(l3, 2)))

    laplace_all = np.zeros((len(alphas), n_runs))
    disc_all = np.zeros((len(discounts), n_runs))
    interp_all = np.zeros(n_runs)
    unsm_all = np.zeros(n_runs)
    best_lams_list = []

    rng = np.random.default_rng(0)
    for r in range(n_runs):
        sents = get_corpus(seed=r)
        idx = np.arange(len(sents))
        rng.shuffle(idx)
        n = len(sents)
        n_tr = int(n * 0.7)
        n_dev = int(n * 0.15)
        train = [sents[i] for i in idx[:n_tr]]
        dev = [sents[i] for i in idx[n_tr : n_tr + n_dev]]
        test = [sents[i] for i in idx[n_tr + n_dev :]]

        res = evaluate_one_split(train, dev, test, alphas, discounts, lambdas_grid)
        laplace_all[:, r] = res["ppl_laplace"]
        disc_all[:, r] = res["ppl_disc"]
        interp_all[r] = res["ppl_interp"]
        unsm_all[r] = res["ppl_unsmoothed"]
        best_lams_list.append(res["best_lams"])

    return dict(
        alphas=alphas,
        discounts=discounts,
        laplace=laplace_all,
        disc=disc_all,
        interp=interp_all,
        unsmoothed=unsm_all,
        best_lams=best_lams_list,
    )


def plot_smoothing(results: dict) -> Path:
    alphas = results["alphas"]
    discounts = results["discounts"]

    lap_mean = results["laplace"].mean(axis=1)
    lap_std = results["laplace"].std(axis=1)
    disc_mean = results["disc"].mean(axis=1)
    disc_std = results["disc"].std(axis=1)
    interp_mean = results["interp"].mean()
    interp_std = results["interp"].std()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ax = axes[0]
    ax.plot(alphas, lap_mean, "o-", linewidth=2, color="C0", label="Laplace bigram")
    ax.fill_between(alphas, lap_mean - lap_std, lap_mean + lap_std,
                    alpha=0.2, color="C0")
    ax.axhline(interp_mean, ls="--", color="C2", linewidth=2,
               label=f"Linear interp. (best lambda on dev) = {interp_mean:.1f}")
    ax.fill_between(alphas, interp_mean - interp_std,
                    interp_mean + interp_std, alpha=0.15, color="C2")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"$\alpha$ (additive smoothing)")
    ax.set_ylabel("test perplexity (log scale)")
    ax.set_title("Laplace: too small alpha undersmooths,\n"
                 "too large alpha oversmooths (U-shape)")
    ax.legend()
    ax.grid(alpha=0.3, which="both")

    ax = axes[1]
    ax.plot(discounts, disc_mean, "s-", linewidth=2, color="C1",
            label="Absolute Discounting bigram")
    ax.fill_between(discounts, disc_mean - disc_std, disc_mean + disc_std,
                    alpha=0.2, color="C1")
    ax.axhline(interp_mean, ls="--", color="C2", linewidth=2,
               label=f"Linear interp. = {interp_mean:.1f}")
    ax.set_xlabel(r"discount $d$")
    ax.set_ylabel("test perplexity")
    ax.set_title("Absolute discounting: mild dependence on d,\n"
                 "all settings beat unsmoothed (inf)")
    ax.legend()
    ax.grid(alpha=0.3)

    fig.suptitle(
        f"Smoothing comparison ({results['laplace'].shape[1]} splits, ±1 std)",
        fontsize=13, fontweight="bold")
    fig.tight_layout()
    out = FIG_DIR / "04_smoothing_comparison.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"[saved] {out}")
    return out


if __name__ == "__main__":
    print("=== 04. Smoothing ===")
    results = run(n_runs=15)

    alphas = results["alphas"]
    discounts = results["discounts"]
    laplace = results["laplace"]
    disc = results["disc"]
    interp = results["interp"]
    unsm = results["unsmoothed"]

    print("\n[Unsmoothed bigram]")
    n_inf = int(np.sum(np.isinf(unsm)))
    print(f"  test ppl is inf in {n_inf}/{len(unsm)} splits "
          f"(eps=0 일 때 unseen bigram 1개만 있어도 inf)")

    print("\n[Laplace bigram, alpha sweep]")
    print(f"  {'alpha':>10} {'mean ppl':>12} {'std':>8}")
    for i, a in enumerate(alphas):
        print(f"  {a:>10.4f} {laplace[i].mean():>12.1f} {laplace[i].std():>8.1f}")
    best_a_idx = int(np.argmin(laplace.mean(axis=1)))
    print(f"  → best alpha = {alphas[best_a_idx]:.4f}, "
          f"min ppl = {laplace[best_a_idx].mean():.1f}")

    print("\n[Absolute Discounting bigram, d sweep]")
    print(f"  {'d':>6} {'mean ppl':>12} {'std':>8}")
    for i, d in enumerate(discounts):
        print(f"  {d:>6.2f} {disc[i].mean():>12.1f} {disc[i].std():>8.1f}")
    best_d_idx = int(np.argmin(disc.mean(axis=1)))
    print(f"  -> best d = {discounts[best_d_idx]:.2f}, "
          f"min ppl = {disc[best_d_idx].mean():.1f}")

    print("\n[Linear Interpolation (trigram+bigram+unigram, lambda via dev grid)]")
    print(f"  test ppl mean ± std = {interp.mean():.1f} ± {interp.std():.1f}")

    from collections import Counter as _C
    c = _C(results["best_lams"])
    print("  most chosen lambda on dev (top 3):")
    for lam, cnt in c.most_common(3):
        print(f"    lambda_tri={lam[0]:.1f}, lambda_bi={lam[1]:.1f}, lambda_uni={lam[2]:.1f}  ×{cnt}")

    print("\n[Summary]")
    print(f"  unsmoothed bigram          = inf  (in {n_inf}/{len(unsm)} splits)")
    print(f"  best Laplace bigram        = {laplace[best_a_idx].mean():>6.1f}  "
          f"(alpha={alphas[best_a_idx]})")
    print(f"  best Abs.Disc bigram       = {disc[best_d_idx].mean():>6.1f}  "
          f"(d={discounts[best_d_idx]})")
    print(f"  Linear Interp (tri+bi+uni) = {interp.mean():>6.1f}")

    plot_smoothing(results)
