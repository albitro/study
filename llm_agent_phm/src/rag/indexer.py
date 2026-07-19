import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


DEFAULT_EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)


def split_markdown(text: str, max_chars: int = 600, overlap: int = 80) -> list[str]:
    blocks: list[tuple[str, str]] = [] 
    current_h1 = ""
    current_h2 = ""
    buf: list[str] = []
    h_path = ""

    def flush():
        if buf:
            blocks.append((h_path, "\n".join(buf).strip()))

    for line in text.splitlines():
        if line.startswith("# "):
            flush(); buf = []
            current_h1 = line.lstrip("# ").strip()
            current_h2 = ""
            h_path = current_h1
        elif line.startswith("## "):
            flush(); buf = []
            current_h2 = line.lstrip("# ").strip()

            
            h_path = f"{current_h1} > {current_h2}" if current_h1 else current_h2
        elif line.startswith("### "):
            flush(); buf = []
            sub = line.lstrip("# ").strip()
            h_path = f"{current_h1} > {current_h2} > {sub}" if current_h2 else f"{current_h1} > {sub}"
        else:
            buf.append(line)
    flush()

    chunks: list[str] = []
    for header, body in blocks:
        if not body:
            continue
        prefix = f"[{header}]\n" if header else ""
        if len(body) <= max_chars:
            chunks.append(prefix + body)
        else:
            start = 0
            while start < len(body):
                end = min(start + max_chars, len(body))
                chunks.append(prefix + body[start:end])
                if end >= len(body):
                    break
                start = end - overlap
    return chunks


def load_docs(docs_dir: str | Path) -> list[Chunk]:
    docs_dir = Path(docs_dir)
    out: list[Chunk] = []
    for md_path in sorted(docs_dir.glob("*.md")):
        text = md_path.read_text(encoding="utf-8")
        doc_id = md_path.stem
        m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        title = m.group(1).strip() if m else doc_id
        for i, c in enumerate(split_markdown(text)):
            out.append(Chunk(
                id=f"{doc_id}#{i}",
                text=c,
                metadata={"source": md_path.name, "title": title, "type": "manual"},
            ))
    return out


class FaissIndexer:
    def __init__(self, model_name: str = DEFAULT_EMBED_MODEL, device: str = "cpu"):
        self.model = SentenceTransformer(model_name, device=device)
        self.dim = self.model.get_sentence_embedding_dimension()
        self.index: faiss.IndexFlatIP | None = None
        self.chunks: list[Chunk] = []

    def build(self, chunks: list[Chunk], batch_size: int = 32) -> "FaissIndexer":
        if not chunks:
            raise ValueError("empty chunks")
        texts = [c.text for c in chunks]
        emb = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
        ).astype("float32")
        self.index = faiss.IndexFlatIP(self.dim)
        self.index.add(emb)
        self.chunks = list(chunks)
        return self

    def save(self, dir_path: str | Path) -> Path:
        dir_path = Path(dir_path)
        dir_path.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(dir_path / "index.faiss"))
        meta = [{"id": c.id, "text": c.text, "metadata": c.metadata} for c in self.chunks]
        (dir_path / "chunks.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8",
        )
        return dir_path

    @classmethod
    def load(cls, dir_path: str | Path, model_name: str = DEFAULT_EMBED_MODEL, device: str = "cpu") -> "FaissIndexer":
        dir_path = Path(dir_path)
        obj = cls(model_name=model_name, device=device)
        obj.index = faiss.read_index(str(dir_path / "index.faiss"))
        meta = json.loads((dir_path / "chunks.json").read_text(encoding="utf-8"))
        obj.chunks = [Chunk(**m) for m in meta]
        return obj
