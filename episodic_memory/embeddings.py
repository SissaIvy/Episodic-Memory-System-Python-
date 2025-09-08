from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import List, Optional


class Embedder(ABC):
    @abstractmethod
    def embed(self, text: str, dim: Optional[int] = None) -> List[float]:
        raise NotImplementedError


class HashEmbedder(Embedder):
    def embed(self, text: str, dim: Optional[int] = None) -> List[float]:
        from .store import _hash_embed  # local import to avoid cycles

        if dim is None:
            dim = 128
        return _hash_embed(text, dim)


class OpenAIEmbedder(Embedder):
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        self.model = model or os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def embed(self, text: str, dim: Optional[int] = None) -> List[float]:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set for OpenAIEmbedder")
        try:
            # OpenAI Python SDK v1.x
            from openai import OpenAI  # type: ignore

            client = OpenAI(api_key=self.api_key)
            resp = client.embeddings.create(model=self.model, input=text)
            vec = resp.data[0].embedding
        except Exception:
            # Fallback: older SDK
            import openai  # type: ignore

            openai.api_key = self.api_key
            resp = openai.Embedding.create(model=self.model, input=text)
            vec = resp["data"][0]["embedding"]

        if dim is not None and dim != len(vec):
            # Downsample or pad with zeros to match requested dim
            if dim < len(vec):
                step = len(vec) / dim
                vec = [vec[int(i * step)] for i in range(dim)]
            else:
                vec = list(vec) + [0.0] * (dim - len(vec))
        return list(map(float, vec))


class SentenceTransformerEmbedder(Embedder):
    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        self.model_name = model_name or os.getenv("SENTENCE_TRANSFORMER_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.device = device or os.getenv("SENTENCE_TRANSFORMER_DEVICE")
        from sentence_transformers import SentenceTransformer  # type: ignore

        self.model = SentenceTransformer(self.model_name, device=self.device)

    def embed(self, text: str, dim: Optional[int] = None) -> List[float]:
        vec = self.model.encode([text], normalize_embeddings=True)[0]
        out = vec.tolist()
        if dim is not None and dim != len(out):
            if dim < len(out):
                step = len(out) / dim
                out = [out[int(i * step)] for i in range(dim)]
            else:
                out = out + [0.0] * (dim - len(out))
        return out


class CachedEmbedder(Embedder):
    def __init__(self, backend: Embedder, backend_name: str, model_id: Optional[str] = None, cache=None):
        from .cache import EmbeddingCache

        self.backend = backend
        self.backend_name = backend_name
        self.model_id = model_id
        self.cache = cache or EmbeddingCache()

    def embed(self, text: str, dim: Optional[int] = None) -> List[float]:
        d = dim or 0
        got = self.cache.get(text, self.backend_name, self.model_id, d)
        if got is not None:
            return got
        vec = self.backend.embed(text, dim)
        self.cache.put(text, self.backend_name, self.model_id, d, vec)
        return vec


def get_embedder(name: str, **kwargs) -> Embedder:
    name = (name or "").lower()
    if name in ("hash", "built-in", "builtin"):
        return HashEmbedder()
    if name in ("openai", "oai"):
        return OpenAIEmbedder(model=kwargs.get("model"), api_key=kwargs.get("api_key"))
    if name in ("st", "sentence-transformers", "local"):
        return SentenceTransformerEmbedder(model_name=kwargs.get("model"), device=kwargs.get("device"))
    raise ValueError(f"Unknown embedder: {name}")
