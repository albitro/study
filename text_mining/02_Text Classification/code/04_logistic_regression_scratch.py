from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

FIG_DIR = Path(__file__).resolve().parent.parent / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def sigmoid(z):
    out = np.empty_like(z, dtype=float)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out


class LogisticRegressionScratch:
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
            diff = y_hat - y
            grad_w = (X.T @ diff) / n + self.lam * self.w_
            grad_b = diff.sum() / n

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
        print("preidct : ",len(self.predict_proba(X)), self.predict_proba(X) >= threshold)
        return (self.predict_proba(X) >= threshold).astype(int)


def make_2d_data(n=300, seed=0):
    rng = np.random.default_rng(seed)
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
    
    print("xx:",xx)
    print("yy:",yy)
    grid = np.c_[xx.ravel(), yy.ravel()]
    print("grid:",grid)
    proba = model.predict_proba(grid).reshape(xx.shape)
    print("proba:", proba)
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


def sentiment_check():
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

    L1 = -np.log(p_pos)
    L0 = -np.log(1 - p_pos)
    print(f"  if y=1,  L_CE = {L1:.4f}   (expected ≈ 0.37)")
    print(f"  if y=0,  L_CE = {L0:.4f}   (expected ≈ 1.17)")


if __name__ == "__main__":
    print("=== 04. Logistic Regression from scratch ===")

    fig = plt.figure(figsize=(16, 5))
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)

    # Part A
    print("\n[A] 2D toy — training & decision boundary")
    final_loss, train_acc = plot_panel_A(ax1, ax2)
    print(f"  final loss  = {final_loss:.4f}")
    print(f"  train acc   = {train_acc:.4f}")

    # Part B
    sentiment_check()

    fig.tight_layout()
    out = FIG_DIR / "04_logistic_regression_scratch.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"\n[saved] {out}")
