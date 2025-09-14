"""Safe wrapper for legacy CLI argument parsing.

Place this alongside your existing CLI parsing code and call
`try_parse_legacy_args(argv)` instead of calling `parse_legacy_args` inside a
broad `except Exception` block.
"""
from __future__ import annotations
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def try_parse_legacy_args(parse_fn, argv: Any) -> Optional[Any]:
    """Call the provided parse function and handle expected failures.

    - parse_fn: a callable like `parse_legacy_args` (dependency-injected to ease testing)
    - argv: the argv to pass

    Returns the parse result, or None for expected parsing failures.
    Unexpected exceptions are re-raised so CI can surface them.
    """
    try:
        return parse_fn(argv)
    except (IndexError, AttributeError, TypeError, ValueError) as e:
        logger.debug("Legacy CLI args parsing failed (expected): %s", e)
        return None
