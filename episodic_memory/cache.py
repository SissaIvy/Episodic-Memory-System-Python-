from __future__ import annotations

import hashlib
import json
from episodic_memory.json_compat import default as json_default
import os
import sqlite3
import threading
from typing import Iterable, Optional


_DDL = """
CREATE TABLE IF NOT EXISTS embeddings (
  key TEXT PRIMARY KEY,
  vector BLOB
);
"""


def _default_path() -> str:
    root = os.getenv("EPISODIC_CACHE_DIR") or os.path.join(os.path.expanduser("~"), ".episodic_cache")
    os.makedirs(root, exist_ok=True)
    return os.path.join(root, "embeddings.sqlite3")


class EmbeddingCache:
    """Simple SQLite-backed embedding cache to reduce CPU/network spikes."""

    def __init__(self, path: Optional[str] = None):
        self.path = path or _default_path()
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False, timeout=5.0)
        with self._conn:
            self._conn.execute(_DDL)
            # Enable WAL for better concurrency; reduce fsync costs
            self._conn.execute("PRAGMA journal_mode=WAL;")
            self._conn.execute("PRAGMA synchronous=NORMAL;")
            self._conn.execute("PRAGMA busy_timeout=5000;")

    def _k(self, text: str, backend: str, model: Optional[str], dim: int) -> str:
        h = hashlib.sha256()
        h.update(text.encode("utf-8"))
        h.update((backend or "").encode("utf-8"))
        h.update((model or "").encode("utf-8"))
        h.update(str(dim).encode("ascii"))
        return h.hexdigest()

    def get(self, text: str, backend: str, model: Optional[str], dim: int) -> Optional[list[float]]:
        key = self._k(text, backend, model, dim)
        with self._lock, self._conn:
            cur = self._conn.execute("SELECT vector FROM embeddings WHERE key=?", (key,))
            row = cur.fetchone()
            if not row:
                return None
            return json.loads(row[0])

    def put(self, text: str, backend: str, model: Optional[str], dim: int, vec: Iterable[float]) -> None:
        key = self._k(text, backend, model, dim)
        # ensure numpy scalars are serialized via json_default
        data = json.dumps(list(vec), default=json_default)
        with self._lock, self._conn:
            self._conn.execute("INSERT OR REPLACE INTO embeddings(key, vector) VALUES (?, ?)", (key, data))

    def close(self) -> None:
        with self._lock:
            try:
                self._conn.close()
            except Exception:
                pass

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass
