from __future__ import annotations

import json
from typing import Any, Optional, Dict


def _find_balanced_json_objects(text: str) -> list[str]:
    """
    Scan the text and collect substrings that are balanced JSON objects.
    Ignores braces inside quoted strings (best-effort, not full JSON parser).
    Returns list of candidate object strings in the order they appear.
    """
    objects: list[str] = []
    in_string = False
    escape = False
    depth = 0
    start_idx: Optional[int] = None
    for i, ch in enumerate(text):
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        # not in string
        if ch == '"':
            in_string = True
            continue
        if ch == '{':
            if depth == 0:
                start_idx = i
            depth += 1
        elif ch == '}':
            if depth > 0:
                depth -= 1
                if depth == 0 and start_idx is not None:
                    objects.append(text[start_idx : i + 1])
                    start_idx = None
    return objects


def extract_last_json_object(text: str) -> Any:
    """
    Returns the last valid JSON object parsed from the given text.
    Raises ValueError if none can be parsed.
    """
    # Fast path: parse directly
    try:
        return json.loads(text)
    except Exception:
        pass

    # Fallback: scan for balanced objects and parse from the end
    candidates = _find_balanced_json_objects(text)
    for blob in reversed(candidates):
        try:
            return json.loads(blob)
        except Exception:
            continue
    raise ValueError("No valid JSON object found in text")


def extract_preamble_fields(text: str) -> Dict[str, Any]:
    """Best-effort extraction of top-level preamble objects like governance before the main JSON object.
    This scans for patterns like '"governance"\\s*:\\s*{...}' and returns parsed dicts.
    """
    out: Dict[str, Any] = {}
    # naive search for governance
    key = '"governance"'
    idx = text.find(key)
    if idx != -1:
        # find the first '{' after the colon
        colon = text.find(':', idx)
        if colon != -1:
            brace = text.find('{', colon)
            if brace != -1:
                # slice from brace to end and parse the first balanced object
                tail = text[brace:]
                objs = _find_balanced_json_objects(tail)
                if objs:
                    try:
                        out["governance"] = json.loads(objs[0])
                    except Exception:
                        pass
    return out


def load_system_from_path(path: str) -> Any:
    """Load the memory system object from a possibly messy JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    obj = extract_last_json_object(data)
    preamble = extract_preamble_fields(data)
    if preamble:
        # Merge governance if missing
        if "governance" in preamble and "governance" not in obj:
            obj["governance"] = preamble["governance"]
    return obj
