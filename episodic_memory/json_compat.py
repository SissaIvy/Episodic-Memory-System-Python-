from __future__ import annotations
"""
JSON compatibility helpers for NumPy types.

- Converts numpy scalar types (e.g., np.float32) to Python builtins via .item()
- Converts numpy arrays to lists via .tolist()
"""
import json
from typing import Any

try:
    import numpy as np  # type: ignore
except Exception:
    np = None  # type: ignore[assignment]


def default(obj: Any) -> Any:
    """Return a JSON-serializable representation for common non-builtin types."""
    # numpy types
    if np is not None:
        # numpy scalar, e.g., np.float32, np.int64
        try:
            if isinstance(obj, getattr(np, "generic", (object,))):
                return obj.item()
        except Exception:
            pass
        # numpy ndarray
        try:
            if isinstance(obj, np.ndarray):
                return obj.tolist()
        except Exception:
            pass
    # common containers
    if isinstance(obj, set):
        return list(obj)
    # Let json raise for unknowns so tests catch real mistakes
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


class NumpyJSONEncoder(json.JSONEncoder):
    """Drop-in encoder if you prefer cls=... over default=..."""
    def default(self, o: Any) -> Any:  # type: ignore[override]
        try:
            return default(o)
        except TypeError:
            return super().default(o)
