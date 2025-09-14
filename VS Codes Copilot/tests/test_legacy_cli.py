import pytest

from src.cli import legacy_args_wrapper as wrapper


def test_try_parse_legacy_args_handles_expected(monkeypatch):
    def boom(_argv):
        raise IndexError("oops")

    assert wrapper.try_parse_legacy_args(boom, []) is None


def test_try_parse_legacy_args_bubbles_unexpected():
    class WeirdError(RuntimeError):
        pass

    def boom(_argv):
        raise WeirdError("unexpected")

    with pytest.raises(RuntimeError):
        wrapper.try_parse_legacy_args(boom, [])
