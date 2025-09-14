"""Score formatting utilities.

Summary:
  Coerce numeric-like scores to JSON-friendly floats rounded to two decimals.

Contracts:
  - Inputs: any type (None, int, float, Decimal, numpy scalar, or other)
  - Outputs: float with two decimals, or None when not convertible
  - Side-effects: none
Errors:
  - Swallows TypeError/ValueError on float conversion by returning None
Example:
  >>> format_score_for_json(1.2345)
  1.23
"""
from __future__ import annotations
from typing import Any, Optional

__all__ = ["format_score_for_json"]


def format_score_for_json(py_score: Any) -> Optional[float]:
    """Return a 2-decimal float suitable for JSON, or None if not numeric-like.

    This explicitly handles None and non-convertible values so the intent is clear
    (instead of inline ternaries scattered across call sites).
    """
    if py_score is None:
        return None
    try:
        num = float(py_score)
    except (TypeError, ValueError):
        return None
    # Round to two decimals (business-friendly); adjust precision if needed.
    return round(num, 2)
