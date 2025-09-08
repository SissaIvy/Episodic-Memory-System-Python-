import argparse
import json
from pathlib import Path

try:
    import pytest  # type: ignore
    HAS_PYTEST = True
except Exception:
    HAS_PYTEST = False

if HAS_PYTEST:
    # Skip gracefully if optional deps missing
    pytest.importorskip("faiss")
    np = pytest.importorskip("numpy")
    memory_cli = pytest.importorskip("memory_cli")

    def make_dummy_json(path: Path, mem_id: str, vec, snippet="hello"):
        data = [{"id": mem_id, "vector": list(vec), "snippet": snippet}]
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)

    @pytest.mark.integration
    def test_persist_meta_end_to_end(tmp_path, capsys):
        # Prepare a small directory of JSON "memories"
        d = tmp_path / "data"
        d.mkdir()
        v1 = np.random.RandomState(0).randn(8).astype("float32")
        v2 = np.random.RandomState(1).randn(8).astype("float32")
        make_dummy_json(d / "a.json", "m1", v1, snippet="snippet A")
        make_dummy_json(d / "b.json", "m2", v2, snippet="snippet B")

        # Build an index from the directory
        idx_out = tmp_path / "idx.faiss"
        build_args = argparse.Namespace(
            data=str(d),
            output=str(idx_out),
            batch_size=256,
            sleep_ms=0,
            positional_input=None,
            path=None,
            index=None,
        )
        # Programmatic wrapper: index_build(args)
        rc = memory_cli.index_build(build_args)
        assert rc == 0
        assert idx_out.exists(), "Index file was not created"

        # Run search with persist_meta -> should write <index>.meta.json
        search_args = argparse.Namespace(
            index=str(idx_out),
            query="snippet",
            top_k=2,
            data=str(d),
            persist_meta=True,
            max_scan=2000,
            min_score=None,
            max_distance=None,
            store=None,
        )
        rc2 = memory_cli.index_search_cli(search_args)
        assert rc2 == 0
        captured = capsys.readouterr()
        out1 = captured.out.strip()
        assert out1, "index_search_cli printed nothing (expected JSON)"

        # meta file dumped adjacent to index
        meta_path = idx_out.with_suffix(idx_out.suffix + ".meta.json")
        assert meta_path.exists(), "Persisted meta file not found after search --persist-meta"

        # Parse JSON result (basic sanity)
        results = json.loads(out1)
        assert isinstance(results, list) and len(results) > 0, "Search returned no results"

        # Now run search again with max_scan=0 (to ensure meta is used and no scanning needed)
        search_args2 = argparse.Namespace(
            index=str(idx_out),
            query="snippet",
            top_k=2,
            data=str(d),
            persist_meta=False,
            max_scan=0,  # forbid scanning if meta absent
            min_score=None,
            max_distance=None,
            store=None,
        )
        rc3 = memory_cli.index_search_cli(search_args2)
        assert rc3 == 0
        captured2 = capsys.readouterr()
        out2 = captured2.out.strip()
        assert out2, "Second search printed nothing; expected JSON results loaded from persisted meta"

        results2 = json.loads(out2)
        assert isinstance(results2, list) and len(results2) > 0, "Second search returned no results using persisted meta"
