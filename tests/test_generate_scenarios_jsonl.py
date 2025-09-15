import io
import json
from pathlib import Path
from contextlib import contextmanager

import pytest

from aml.components import generate_scenarios


def test_generates_expected_event_count(tmp_path, monkeypatch):
    out = io.StringIO()

    # Fake a simple args object
    class A:
        pass

    args = A()
    args.seed = 1
    args.n_events = 5
    args.out_path = str(tmp_path / "out.jsonl")

    # Provide a context manager that yields the StringIO but doesn't close it on exit
    @contextmanager
    def _stringio_ctx(buf):
        yield buf

    # Patch open to capture writes to the file path; return a non-closing context manager for the target path
    def fake_open(path, mode="r", encoding=None):
        # Return the in-memory buffer for writes to out_path (as a context manager)
        if str(path) == args.out_path:
            return _stringio_ctx(out)
        # fallback to real open for others
        return open(path, mode, encoding=encoding)

    monkeypatch.setattr("pathlib.Path.open", lambda self, mode='r', encoding=None: fake_open(str(self), mode, encoding))

    # Call main with simulated args via monkeypatching argparse
    monkeypatch.setattr("argparse.ArgumentParser.parse_args", lambda self: args)
    generate_scenarios.main()

    lines = [json.loads(s) for s in out.getvalue().splitlines() if s.strip()]
    assert len(lines) == args.n_events
