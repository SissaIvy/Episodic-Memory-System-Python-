from __future__ import annotations

import json
import math
import os
import time
from typing import List, Tuple, Optional


class _MissingFaiss(Exception):
    pass


def _ensure_faiss():
    try:
        import faiss  # type: ignore
        import numpy as np  # type: ignore
        return faiss, np
    except Exception as e:
        raise _MissingFaiss("FAISS or numpy not installed. Install with: pip install -e .[faiss]") from e


def _normalize(vecs):
    import numpy as np  # type: ignore

    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vecs / norms


class FaissIndexManager:
    def __init__(self, dim: int):
        faiss, np = _ensure_faiss()
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)
        self.ids: List[str] = []

    def add_vectors(self, ids: List[str], vectors: List[List[float]], batch_size: int = 1024, sleep_ms: int = 0) -> None:
        faiss, np = _ensure_faiss()
        assert len(ids) == len(vectors)
        for i in range(0, len(ids), batch_size):
            chunk_ids = ids[i:i + batch_size]
            chunk_vecs = vectors[i:i + batch_size]
            arr = np.array(chunk_vecs, dtype="float32")
            arr = _normalize(arr)
            self.index.add(arr)
            self.ids.extend(chunk_ids)
            if sleep_ms:
                time.sleep(sleep_ms / 1000.0)

    def search(self, query: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        faiss, np = _ensure_faiss()
        q = np.array([query], dtype="float32")
        q = _normalize(q)
        scores, idxs = self.index.search(q, top_k)
        res: List[Tuple[str, float]] = []
        for s, i in zip(scores[0].tolist(), idxs[0].tolist()):
            if i == -1:
                continue
            if i < len(self.ids):
                res.append((self.ids[i], float(s)))
        return res

    def save(self, index_path: str) -> None:
        faiss, np = _ensure_faiss()
        meta_path = index_path + ".meta.json"
        faiss.write_index(self.index, index_path)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({"dim": self.dim, "ids": self.ids}, f)

    @staticmethod
    def load(index_path: str) -> "FaissIndexManager":
        faiss, np = _ensure_faiss()
        meta_path = index_path + ".meta.json"
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        mgr = FaissIndexManager(dim=int(meta["dim"]))
        mgr.index = faiss.read_index(index_path)
        mgr.ids = list(meta["ids"])  # type: ignore
        return mgr

    @staticmethod
    def build_from_store(store, batch_size: int = 1024, sleep_ms: int = 0) -> "FaissIndexManager":
        dim = store.system.system_metadata.embedding_dimension
        mgr = FaissIndexManager(dim)
        ids: List[str] = []
        vecs: List[List[float]] = []
        for mem_id, entry in store.system.memory_entries.items():
            v = entry.encoded_experience.vector_embedding
            if not v:
                continue
            ids.append(mem_id)
            vecs.append([float(x) for x in v])
        mgr.add_vectors(ids, vecs, batch_size=batch_size, sleep_ms=sleep_ms)
        return mgr

