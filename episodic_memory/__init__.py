"""
Episodic Memory System (minimal, dependency-free)

This package provides:
- Robust JSON loader that extracts the last valid object from a mixed file
- In-memory store with simple vector embedding and retrieval
- Basic scoring that combines similarity, recency, and importance

Intended for demonstration and extension for production use.
"""

from .store import MemoryStore, RetrievalResult
from .utils import load_system_from_path
from .embeddings import get_embedder, HashEmbedder, OpenAIEmbedder
from .schema import load_schema, validate_instance

__all__ = [
    "MemoryStore",
    "RetrievalResult",
    "load_system_from_path",
    "get_embedder",
    "HashEmbedder",
    "OpenAIEmbedder",
    "load_schema",
    "validate_instance",
]
