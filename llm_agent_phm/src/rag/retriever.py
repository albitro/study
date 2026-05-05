import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .indexer import FaissIndexer, Chunk


@dataclass
class SearchHit:
    chunk: Chunk
    score: float


_TOKEN_RE = re.compile(r"[A-Za-z0-9]+|[가-힣]+")


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


class HybridRetriever:
    def __init__(self, indexer: FaissIndexer, alpha: float = 0.7):
        self.indexer = indexer
        self.alpha = alpha
        self._idf = self._compute_idf()

    def _compute_idf(self) -> dict[str, float]:
        n_docs = len(self.indexer.chunks)
        df: Counter[str] = Counter()
        for c in self.indexer.chunks:
            for tok in set(_tokenize(c.text)):
                df[tok] += 1
        return {t: math.log((n_docs + 1) / (f + 1)) + 1 for t, f in df.items()}

    def _kw_score(self, query: str, text: str) -> float:
        q_toks = set(_tokenize(query))
        if not q_toks:
            return 0.0
        t_toks = Counter(_tokenize(text))
        score = 0.0
        for tok in q_toks:
            if tok in t_toks:
                score += self._idf.get(tok, 1.0) * (1 + math.log(t_toks[tok]))
        denom = sum(self._idf.get(t, 1.0) for t in q_toks) or 1.0
        return min(1.0, score / denom)

    def search(
        self,
        query: str,
        k: int = 5,
        candidates: int = 20,
        filter_metadata: dict | None = None,
    ) -> list[SearchHit]:
        if self.indexer.index is None:
            raise RuntimeError("indexer not built/loaded")

        q_emb = self.indexer.model.encode(
            [query], normalize_embeddings=True, convert_to_numpy=True
        ).astype("float32")
        sims, ids = self.indexer.index.search(q_emb, candidates)
        sims, ids = sims[0], ids[0]

        hits: list[SearchHit] = []
        for sim, idx in zip(sims, ids):
            if idx < 0:
                continue
            c = self.indexer.chunks[idx]
            if filter_metadata and not _match_meta(c.metadata, filter_metadata):
                continue
            kw = self._kw_score(query, c.text)
            final = self.alpha * float(sim) + (1 - self.alpha) * kw
            hits.append(SearchHit(chunk=c, score=final))

        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:k]


def _match_meta(meta: dict, filt: dict) -> bool:
    for k, v in filt.items():
        if meta.get(k) != v:
            return False
    return True


def load_retriever(index_dir: str | Path, alpha: float = 0.7) -> HybridRetriever:
    return HybridRetriever(FaissIndexer.load(index_dir), alpha=alpha)
