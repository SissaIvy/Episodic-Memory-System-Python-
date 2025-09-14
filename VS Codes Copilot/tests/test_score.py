import pytest

# Adjust this import to your project layout if needed:
from src.utils.score import format_score_for_json


def test_format_score_for_json_none_and_bad_values():
    assert format_score_for_json(None) is None
    assert format_score_for_json("not-a-number") is None


def test_format_score_for_json_numeric_values():
    assert format_score_for_json(1.2345) == 1.23
    assert format_score_for_json(1) == 1.00
    # Float edge: ensure normal rounding semantics
    assert format_score_for_json(2.675) in (2.67, 2.68)


@pytest.mark.parametrize("value,expected", [(0, 0.00), (-1.234, -1.23), (123456.789, 123456.79)])
def test_format_score_for_json_parametrized(value, expected):
    assert format_score_for_json(value) == expected
