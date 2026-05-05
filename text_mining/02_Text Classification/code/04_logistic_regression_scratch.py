"""
04_logistic_regression_scratch.py
=================================
Logistic Regression 을 NumPy scratch 로 구현.

학습 목표
---------
1. Sigmoid, forward pass, Cross-Entropy loss 직접 계산.
2. Gradient (슬라이드 공식) dL/dw_j = Σ (ŷ_i - y_i) x_{i,j} 검증.
3. Gradient descent 로 수렴하는 과정 — loss 가 단조 감소 (convex).
4. Regularization (L2) 유무에 따른 일반화 성능 차이.

실험 구성
---------
Part A: 2D toy 데이터에서 decision boundary 학습 시각화 (loss curve + boundary)
Part B: 강의 예시의 6차원 sentiment feature vector 재현
        x = [3, 2, 1, 3, 0, 4.19], w = [2.5, -5.0, -1.2, 0.5, 2.0, 0.7], b = 0.1
        → σ(0.8) ≈ 0.69 (강의 수치와 일치하는지 sanity check)
Part C: L2 regularization 강도 (λ) 를 바꿔가며 test accuracy 스윕

실행: python scripts/04_logistic_regression_scratch.py
결과: figures/04_logistic_regression_scratch.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

FIG_DIR = Path(__file__).resolve().parent.parent / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------------------
# Scratch Logistic Regression
# -------------------------------------------------------------
def sigmoid(z):
    # 수치안정: 큰 양/음수에서도 안전
    out = np.empty_like(z, dtype=float)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out


class LogisticRegressionScratch:
    """
    이진 Logistic Regression (scratch).
        z = w · x + b
        ŷ = σ(z)
        L = -Σ [y log ŷ + (1-y) log(1-ŷ)]  + (λ/2) ||w||²
        dL/dw = Σ (ŷ - y) x  + λw
        dL/db = Σ (ŷ - y)
    """

    def __init__(self, lr=0.1, n_epochs=500, lam=0.0, verbose=False):
        self.lr = lr
        self.n_epochs = n_epochs
        self.lam = lam
        self.verbose = verbose
        self.w_ = None
        self.b_ = None
        self.loss_history_ = []

    def _ce_loss(self, y, y_hat):
        eps = 1e-12
        y_hat = np.clip(y_hat, eps, 1 - eps)
        ce = -np.mean(y * np.log(y_hat) + (1 - y) * np.log(1 - y_hat))
        reg = 0.5 * self.lam * np.sum(self.w_ ** 2) / len(y)
        return ce + reg

    def fit(self, X, y):
        n, d = X.shape
        self.w_ = np.zeros(d)
        self.b_ = 0.0
        self.loss_history_ = []

        for epoch in range(self.n_epochs):
            z = X @ self.w_ + self.b_
            y_hat = sigmoid(z)
            # gradient: CE 부분은 평균, L2 는 그대로
            diff = y_hat - y
            grad_w = (X.T @ diff) / n + self.lam * self.w_
            grad_b = diff.sum() / n
            # 업데이트
            self.w_ -= self.lr * grad_w
            self.b_ -= self.lr * grad_b

            self.loss_history_.append(self._ce_loss(y, y_hat))
            if self.verbose and (epoch + 1) % 100 == 0:
                print(f"  epoch {epoch+1:4d}  loss = "
                      f"{self.loss_history_[-1]:.4f}")
        return self

    def predict_proba(self, X):
        return sigmoid(X @ self.w_ + self.b_)

    def predict(self, X, threshold=0.5):
        return (self.predict_proba(X) >= threshold).astype(int)


# -------------------------------------------------------------
# Part A: 2D toy + loss curve + decision boundary
# -------------------------------------------------------------
def make_2d_data(n=300, seed=0):
    rng = np.random.default_rng(seed)
    # 두 개의 가우시안 클러스터 (약간 겹치도록)
    mu0, mu1 = np.array([-1.2, -0.5]), np.array([1.2, 0.8])
    X0 = rng.normal(mu0, 1.0, size=(n // 2, 2))
    X1 = rng.normal(mu1, 1.0, size=(n // 2, 2))
    X = np.vstack([X0, X1])
    y = np.array([0] * (n // 2) + [1] * (n // 2))
    perm = rng.permutation(n)
    return X[perm], y[perm]


def plot_panel_A(ax_loss, ax_boundary):
    X, y = make_2d_data(n=300, seed=0)
    model = LogisticRegressionScratch(lr=0.1, n_epochs=500, lam=0.0)
    model.fit(X, y)

    # 1) loss curve
    ax_loss.plot(model.loss_history_, linewidth=2, color="C0")
    ax_loss.set_xlabel("epoch")
    ax_loss.set_ylabel("cross-entropy loss")
    ax_loss.set_title(
        f"Loss decreases monotonically (convex)\n"
        f"final loss = {model.loss_history_[-1]:.4f}"
    )
    ax_loss.grid(alpha=0.3)

    # 2) decision boundary
    x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
    y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 300),
                          np.linspace(y_min, y_max, 300))
    grid = np.c_[xx.ravel(), yy.ravel()]
    proba = model.predict_proba(grid).reshape(xx.shape)

    ax_boundary.contourf(xx, yy, proba, levels=20,
                         cmap="coolwarm", alpha=0.35)
    ax_boundary.contour(xx, yy, proba, levels=[0.5],
                        colors="k", linewidths=2)
    ax_boundary.scatter(X[y == 0, 0], X[y == 0, 1],
                        c="C0", s=15, label="y=0", alpha=0.7)
    ax_boundary.scatter(X[y == 1, 0], X[y == 1, 1],
                        c="C3", s=15, label="y=1", alpha=0.7)
    train_acc = (model.predict(X) == y).mean()
    ax_boundary.set_title(
        f"Learned decision boundary   (train acc = {train_acc:.3f})"
    )
    ax_boundary.legend(loc="lower right")
    ax_boundary.grid(alpha=0.3)
    ax_boundary.set_xlabel(r"$x_1$")
    ax_boundary.set_ylabel(r"$x_2$")

    return model.loss_history_[-1], train_acc


# -------------------------------------------------------------
# Part B: 강의 sentiment 예시 sanity check
# -------------------------------------------------------------
def lecture_sentiment_check():
    # 강의: x = [3, 2, 1, 3, 0, 4.19], w = [2.5,-5,-1.2,0.5,2,0.7], b = 0.1
    # NB 강의 슬라이드 계산:  z = 0.805,  σ(z) ≈ 0.69
    x = np.array([3, 2, 1, 3, 0, 4.19])
    w = np.array([2.5, -5.0, -1.2, 0.5, 2.0, 0.7])
    b = 0.1
    z = w @ x + b
    p_pos = sigmoid(np.array([z]))[0]
    print("\n[Lecture sanity check]")
    print(f"  z = w·x + b = {z:.4f}")
    print(f"  σ(z) = P(y=1|x) = {p_pos:.4f}   "
          f"(expected ≈ 0.69)")
    print(f"  P(y=0|x) = {1 - p_pos:.4f}   (expected ≈ 0.31)")

    # CE loss sanity
    # y = 1 → L = -log(0.69) ≈ 0.37
    # y = 0 → L = -log(0.31) ≈ 1.17
    L1 = -np.log(p_pos)
    L0 = -np.log(1 - p_pos)
    print(f"  if y=1,  L_CE = {L1:.4f}   (expected ≈ 0.37)")
    print(f"  if y=0,  L_CE = {L0:.4f}   (expected ≈ 1.17)")


# -------------------------------------------------------------
# Part C: L2 regularization 스윕
# -------------------------------------------------------------
def make_high_dim_data(n=150, d=100, n_signal=3, label_noise=0.0, seed=0):
    """
    n_signal 개 '진짜' 신호 + (d - n_signal) 개 noise feature.
    """
    rng = np.random.default_rng(seed)
    X_signal = rng.normal(0, 1, size=(n, n_signal))
    true_w = np.array([2.0, -2.0, 2.0][:n_signal])
    z = X_signal @ true_w
    y = (z > 0).astype(int)

    flip = rng.uniform(size=n) < label_noise
    y = np.where(flip, 1 - y, y)

    X_noise = rng.normal(0, 1, size=(n, d - n_signal))
    X = np.hstack([X_signal, X_noise])
    return X, y


def lambda_sweep(lambdas, n_runs=30):
    """
    Separable 데이터에서 LR 은 λ=0 이면 weight norm 이 계속 커지면서 수렴.
    λ>0 이면 weight norm 이 유한하게 유지됨. 이 실험은 이 효과를 명시적으로
    측정한다.
    """
    train_accs = np.zeros((len(lambdas), n_runs))
    test_accs = np.zeros((len(lambdas), n_runs))
    w_norms = np.zeros((len(lambdas), n_runs))
    for r in range(n_runs):
        X_tr, y_tr = make_high_dim_data(
            n=30, d=80, n_signal=3, label_noise=0.1, seed=3000 + r,
        )
        X_te, y_te = make_high_dim_data(
            n=500, d=80, n_signal=3, label_noise=0.0, seed=7000 + r,
        )

        for i, lam in enumerate(lambdas):
            clf = LogisticRegressionScratch(
                lr=0.1, n_epochs=3000, lam=lam,
            ).fit(X_tr, y_tr)
            train_accs[i, r] = (clf.predict(X_tr) == y_tr).mean()
            test_accs[i, r] = (clf.predict(X_te) == y_te).mean()
            w_norms[i, r] = np.linalg.norm(clf.w_)
    return train_accs, test_accs, w_norms


def plot_panel_C(ax, lambdas, train_accs, test_accs, w_norms):
    tr_mean, tr_std = train_accs.mean(1), train_accs.std(1)
    te_mean, te_std = test_accs.mean(1), test_accs.std(1)
    wn_mean = w_norms.mean(1)

    xs_plot = np.array([l if l > 0 else 1e-5 for l in lambdas])

    # 왼쪽 축: accuracy
    ax.plot(xs_plot, tr_mean, "o-", linewidth=2, color="C0",
            label="train accuracy")
    ax.fill_between(xs_plot, tr_mean - tr_std, tr_mean + tr_std,
                    alpha=0.2, color="C0")
    ax.plot(xs_plot, te_mean, "s-", linewidth=2, color="C3",
            label="test accuracy")
    ax.fill_between(xs_plot, te_mean - te_std, te_mean + te_std,
                    alpha=0.2, color="C3")
    ax.set_xscale("log")
    ax.set_xlabel(r"L2 strength $\lambda$  (first point = $\lambda=0$)")
    ax.set_ylabel("accuracy")
    ax.grid(alpha=0.3)
    ax.legend(loc="lower left")

    # 오른쪽 축: weight norm
    ax2 = ax.twinx()
    ax2.plot(xs_plot, wn_mean, "^--", linewidth=1.5,
             color="C2", alpha=0.7, label=r"$\|w\|_2$")
    ax2.set_ylabel(r"weight norm $\|w\|_2$", color="C2")
    ax2.tick_params(axis="y", labelcolor="C2")
    ax2.legend(loc="upper right")

    ax.set_title(r"L2 shrinks $\|w\|_2$ (green): $\lambda\uparrow \Rightarrow \|w\|\downarrow$")


# -------------------------------------------------------------
# Main
# -------------------------------------------------------------
if __name__ == "__main__":
    print("=== 04. Logistic Regression from scratch ===")

    fig = plt.figure(figsize=(16, 5))
    ax1 = fig.add_subplot(1, 3, 1)
    ax2 = fig.add_subplot(1, 3, 2)
    ax3 = fig.add_subplot(1, 3, 3)

    # Part A
    print("\n[A] 2D toy — training & decision boundary")
    final_loss, train_acc = plot_panel_A(ax1, ax2)
    print(f"  final loss  = {final_loss:.4f}")
    print(f"  train acc   = {train_acc:.4f}")

    # Part B
    lecture_sentiment_check()

    # Part C
    print("\n[C] L2 regularization sweep (weight norm shrinkage)")
    lambdas = [0.0, 0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
    train_accs, test_accs, w_norms = lambda_sweep(lambdas, n_runs=30)
    print(f"  {'lambda':>7}  {'train':>7}  {'test':>7}  {'||w||':>7}")
    for l, tr, te, wn in zip(lambdas,
                              train_accs.mean(1), test_accs.mean(1),
                              w_norms.mean(1)):
        print(f"  {l:>7g}  {tr:>7.4f}  {te:>7.4f}  {wn:>7.3f}")
    print(f"  → λ=0:  ||w|| = {w_norms.mean(1)[0]:.2f}  "
          f"(gradient descent can keep growing w on separable data)")
    print(f"  → λ=5:  ||w|| = {w_norms.mean(1)[-1]:.2f}  "
          f"← L2 shrinks weight norm (key effect)")

    plot_panel_C(ax3, lambdas, train_accs, test_accs, w_norms)

    fig.suptitle(
        "Scratch Logistic Regression: convex loss, learned boundary, "
        "L2 effect", fontsize=12,
    )
    fig.tight_layout()
    out = FIG_DIR / "04_logistic_regression_scratch.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"\n[saved] {out}")
    print("\nDone.")
