from __future__ import annotations

import json
import os
from typing import Any, Tuple
from importlib import resources


def load_schema(path: str | None = None) -> dict:
    if path is None:
        try:
            data = resources.files("episodic_memory.schemas").joinpath("episodic_memory.schema.json").read_text(encoding="utf-8")
            return json.loads(data)
        except Exception:
            # Fallback to file path relative to package
            path = os.path.join(os.path.dirname(__file__), "schemas", "episodic_memory.schema.json")
            path = os.path.normpath(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_instance(instance: Any, schema: dict | None = None) -> Tuple[bool, str | None]:
    try:
        import jsonschema  # type: ignore
    except Exception:
        return False, "jsonschema package not installed. Install with: pip install jsonschema"

    if schema is None:
        schema = load_schema()
    try:
        Validator = jsonschema.Draft202012Validator  # type: ignore
        checker = jsonschema.FormatChecker()  # type: ignore
        Validator(schema, format_checker=checker).validate(instance)
        return True, None
    except jsonschema.ValidationError as e:  # type: ignore
        return False, str(e)
