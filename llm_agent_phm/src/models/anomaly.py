import json
from dataclasses import dataclass, asdict
from pathlib import Path

import joblib
import numpy as np
import torch
import torch.nn as nn
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def window_stats(windows: np.ndarray) -> np.ndarray:
    N, T, C = windows.shape
    feats = np.empty((N, C * 6), dtype=np.float32)

    mean = windows.mean(axis=1)
    std = windows.std(axis=1)
    mn = windows.min(axis=1)
    mx = windows.max(axis=1)
    p2p = mx - mn

    t = np.arange(T, dtype=np.float32)
    t_mean = t.mean()
    t_var = ((t - t_mean) ** 2).sum()
    centered = windows - mean[:, None, :]
    slope = ((t - t_mean)[None, :, None] * centered).sum(axis=1) / t_var

    feats[:, 0::6] = mean
    feats[:, 1::6] = std
    feats[:, 2::6] = mn
    feats[:, 3::6] = mx
    feats[:, 4::6] = p2p
    feats[:, 5::6] = slope
    return feats


@dataclass
class IFConfig:
    n_estimators: int = 200
    contamination: float | str = "auto"
    random_state: int = 42


class IFAnomalyModel:
    def __init__(self, cfg: IFConfig | None = None):
        self.cfg = cfg or IFConfig()
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            n_estimators=self.cfg.n_estimators,
            contamination=self.cfg.contamination,
            random_state=self.cfg.random_state,
            n_jobs=-1,
        )

    def fit(self, windows_normal: np.ndarray) -> "IFAnomalyModel":
        feats = window_stats(windows_normal)
        feats = self.scaler.fit_transform(feats)
        self.model.fit(feats)
        return self

    def score(self, windows: np.ndarray) -> np.ndarray:
        feats = self.scaler.transform(window_stats(windows))
        return -self.model.decision_function(feats)

    def predict(self, windows: np.ndarray, threshold: float) -> np.ndarray:
        return (self.score(windows) > threshold).astype(np.int8)

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"scaler": self.scaler, "model": self.model, "cfg": asdict(self.cfg)}, path)

    @classmethod
    def load(cls, path: str | Path) -> "IFAnomalyModel":
        data = joblib.load(path)
        obj = cls(IFConfig(**data["cfg"]))
        obj.scaler = data["scaler"]
        obj.model = data["model"]
        return obj


class ConvAE(nn.Module):
    def __init__(self, n_channels: int, hidden: int = 32, latent: int = 16):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv1d(n_channels, hidden, kernel_size=5, stride=2, padding=2),
            nn.ReLU(),
            nn.Conv1d(hidden, hidden * 2, kernel_size=5, stride=2, padding=2),
            nn.ReLU(),
            nn.Conv1d(hidden * 2, latent, kernel_size=3, stride=1, padding=1),
        )
        self.decoder = nn.Sequential(
            nn.ConvTranspose1d(latent, hidden * 2, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.ConvTranspose1d(hidden * 2, hidden, kernel_size=5, stride=2, padding=2, output_padding=1),
            nn.ReLU(),
            nn.ConvTranspose1d(hidden, n_channels, kernel_size=5, stride=2, padding=2, output_padding=1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.encoder(x)
        out = self.decoder(z)
        return out[..., : x.shape[-1]]


@dataclass
class AEConfig:
    n_channels: int = 7
    hidden: int = 32
    latent: int = 16
    lr: float = 1e-3
    epochs: int = 30
    batch_size: int = 128
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    per_window_norm: bool = True


class AEAnomalyModel:
    def __init__(self, cfg: AEConfig | None = None):
        self.cfg = cfg or AEConfig()
        self.scaler_mean: np.ndarray | None = None
        self.scaler_std: np.ndarray | None = None
        self.model = ConvAE(self.cfg.n_channels, self.cfg.hidden, self.cfg.latent).to(self.cfg.device)

    @staticmethod
    def _per_window_zscore(X: np.ndarray, eps: float = 1e-6) -> np.ndarray:
        mean = X.mean(axis=1, keepdims=True)
        std = X.std(axis=1, keepdims=True)
        return ((X - mean) / (std + eps)).astype(np.float32)

    def _preprocess(self, windows: np.ndarray) -> np.ndarray:
        if self.cfg.per_window_norm:
            return self._per_window_zscore(windows)
        return ((windows - self.scaler_mean) / (self.scaler_std + 1e-6)).astype(np.float32)

    def fit(self, windows_normal: np.ndarray) -> "AEAnomalyModel":
        if self.cfg.per_window_norm:
            self.scaler_mean = np.zeros((1, 1, self.cfg.n_channels), dtype=np.float32)
            self.scaler_std = np.ones((1, 1, self.cfg.n_channels), dtype=np.float32)
        else:
            self.scaler_mean = windows_normal.mean(axis=(0, 1), keepdims=True)
            self.scaler_std = windows_normal.std(axis=(0, 1), keepdims=True)

        x = self._preprocess(windows_normal)
        x = np.transpose(x, (0, 2, 1))

        ds = torch.utils.data.TensorDataset(torch.from_numpy(x))
        dl = torch.utils.data.DataLoader(ds, batch_size=self.cfg.batch_size, shuffle=True, drop_last=True)

        opt = torch.optim.Adam(self.model.parameters(), lr=self.cfg.lr)
        loss_fn = nn.MSELoss()

        self.model.train()
        for ep in range(self.cfg.epochs):
            tot, n = 0.0, 0
            for (xb,) in dl:
                xb = xb.to(self.cfg.device)
                recon = self.model(xb)
                loss = loss_fn(recon, xb)
                opt.zero_grad()
                loss.backward()
                opt.step()
                tot += loss.item() * xb.size(0)
                n += xb.size(0)
            if (ep + 1) % 5 == 0 or ep == 0:
                print(f"  epoch {ep+1:3d}/{self.cfg.epochs} | loss={tot/n:.4f}")
        return self

    @torch.no_grad()
    def score(self, windows: np.ndarray) -> np.ndarray:
        self.model.eval()
        x = self._preprocess(windows)
        x = np.transpose(x, (0, 2, 1))
        x_t = torch.from_numpy(x).to(self.cfg.device)
        recon = self.model(x_t)
        err = ((recon - x_t) ** 2).mean(dim=(1, 2)).cpu().numpy()
        return err

    @torch.no_grad()
    def per_channel_error(self, windows: np.ndarray) -> np.ndarray:
        self.model.eval()
        x = self._preprocess(windows)
        x = np.transpose(x, (0, 2, 1))
        x_t = torch.from_numpy(x).to(self.cfg.device)
        recon = self.model(x_t)
        err = ((recon - x_t) ** 2).mean(dim=2).cpu().numpy()
        return err

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "state_dict": self.model.state_dict(),
                "cfg": asdict(self.cfg),
                "scaler_mean": self.scaler_mean,
                "scaler_std": self.scaler_std,
            },
            path,
        )

    @classmethod
    def load(cls, path: str | Path, device: str | None = None) -> "AEAnomalyModel":
        data = torch.load(path, map_location=device or "cpu", weights_only=False)
        cfg = AEConfig(**data["cfg"])
        if device:
            cfg.device = device
        obj = cls(cfg)
        obj.model.load_state_dict(data["state_dict"])
        obj.model.to(cfg.device)
        obj.scaler_mean = data["scaler_mean"]
        obj.scaler_std = data["scaler_std"]
        return obj


def find_best_threshold(scores: np.ndarray, labels: np.ndarray) -> tuple[float, dict]:
    from sklearn.metrics import f1_score, precision_score, recall_score, average_precision_score

    qs = np.quantile(scores, np.linspace(0.5, 0.999, 200))
    best = (0.0, -1.0, {})
    for thr in qs:
        pred = (scores > thr).astype(np.int8)
        if pred.sum() == 0:
            continue
        f1 = f1_score(labels, pred, zero_division=0)
        if f1 > best[1]:
            best = (
                float(thr),
                float(f1),
                {
                    "precision": float(precision_score(labels, pred, zero_division=0)),
                    "recall": float(recall_score(labels, pred, zero_division=0)),
                    "f1": float(f1),
                    "pr_auc": float(average_precision_score(labels, scores)),
                },
            )
    return best[0], best[2]
