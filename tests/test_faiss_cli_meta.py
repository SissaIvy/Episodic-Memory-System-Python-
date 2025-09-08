import json
import argparse
from pathlib import Path
try:
    import numpy as np  # type: ignore
    HAS_NUMPY = True
except Exception:
    HAS_NUMPY = False
import importlib
try:
    import pytest  # type: ignore
except Exception:  # pragma: no cover
    pytest = None

try:
    import faiss  # noqa: F401, type: ignore
    HAS_FAISS = True
except Exception:
    HAS_FAISS = False

# If pytest is available, mark skip; otherwise runtime-guard inside test
if pytest is not None:
    pytestmark = pytest.mark.skipif(not (HAS_FAISS and HAS_NUMPY), reason="FAISS/NumPy not installed")

memory_cli = importlib.import_module("memory_cli")


def make_dummy_json(path: Path, mem_id: str, vec):
    data = [{"id": mem_id, "vector": list(vec), "snippet": f"snippet for {mem_id}"}]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def test_index_build_and_search_with_meta(tmp_path: Path):
    if not (HAS_FAISS and HAS_NUMPY):
        # Fallback for unittest discovery without extras
        return
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    v1 = np.random.RandomState(0).randn(8).astype("float32")
    v2 = np.random.RandomState(1).randn(8).astype("float32")
    make_dummy_json(a, "m1", v1)
    make_dummy_json(b, "m2", v2)

    args = argparse.Namespace(
        data=str(tmp_path),
        output=str(tmp_path / "idx.faiss"),
        batch_size=256,
        sleep_ms=0,
        positional_input=None,
        path=None,
        index=None,
    )
    rc = memory_cli.index_build(args)
    assert rc == 0

    search_args = argparse.Namespace(
        index=str(tmp_path / "idx.faiss"),
        query="whatever",
        top_k=2,
        data=str(tmp_path),
    )
    # Run; function prints JSON to stdout. This ensures no exceptions.
    rc2 = memory_cli.index_search_cli(search_args)
    assert rc2 == 0
