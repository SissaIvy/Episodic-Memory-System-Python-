import json
import pytest

try:
    import numpy as np  # type: ignore
except Exception:
    np = None

from episodic_memory.json_compat import default


@pytest.mark.skipif(np is None, reason="numpy not available")
def test_numpy_scalar_is_json_safe():
    s = json.dumps({"x": np.float32(1.5)}, default=default)
    assert s == '{"x": 1.5}'


@pytest.mark.skipif(np is None, reason="numpy not available")
def test_numpy_array_is_json_safe():
    s = json.dumps({"arr": np.array([1, 2, 3], dtype=np.int32)}, default=default)
    assert s == '{"arr": [1, 2, 3]}'
