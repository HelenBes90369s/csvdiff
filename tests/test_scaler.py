"""Tests for csvdiff.scaler."""
import pytest
from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.scaler import ScaleError, scale_diff


def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key, kind="changed", fcs=None):
    return RowChange(key=key, kind=kind, field_changes=fcs or [])


def make_result(added=None, removed=None, changed=None):
    return DiffResult(
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


def test_scale_none_raises():
    with pytest.raises(ScaleError):
        scale_diff(None)


def test_scale_empty_result_returns_empty():
    result = make_result()
    assert scale_diff(result) == []


def test_scale_non_numeric_delta_is_none():
    rc = _change(("1",), fcs=[_fc("name", "Alice", "Bob")])
    result = make_result(changed=[rc])
    out = scale_diff(result)
    assert len(out) == 1
    sf = out[0].fields[0]
    assert sf.raw_delta is None
    assert sf.scaled_delta is None


def test_scale_single_numeric_change_range_zero_gives_none_scaled():
    # Only one value → range == 0 → scaled_delta is None
    rc = _change(("1",), fcs=[_fc("score", "10", "20")])
    result = make_result(changed=[rc])
    out = scale_diff(result)
    sf = out[0].fields[0]
    assert sf.raw_delta == pytest.approx(10.0)
    assert sf.scaled_delta is None


def test_scale_two_changes_normalised_correctly():
    rc1 = _change(("1",), fcs=[_fc("score", "0", "10")])
    rc2 = _change(("2",), fcs=[_fc("score", "0", "30")])
    result = make_result(changed=[rc1, rc2])
    out = scale_diff(result)
    # deltas: 10 and 30 → min=10, range=20
    s1 = out[0].fields[0].scaled_delta
    s2 = out[1].fields[0].scaled_delta
    assert s1 == pytest.approx(0.0)
    assert s2 == pytest.approx(1.0)


def test_scale_added_row_included():
    rc = _change(("3",), kind="added", fcs=[_fc("val", "", "5")])
    result = make_result(added=[rc])
    out = scale_diff(result)
    assert len(out) == 1
    assert out[0].kind == "added"


def test_scale_removed_row_included():
    rc = _change(("4",), kind="removed", fcs=[_fc("val", "9", "")])
    result = make_result(removed=[rc])
    out = scale_diff(result)
    assert len(out) == 1
    assert out[0].kind == "removed"


def test_scale_preserves_key_and_kind():
    rc = _change(("x", "y"), kind="changed", fcs=[_fc("n", "1", "2")])
    result = make_result(changed=[rc])
    out = scale_diff(result)
    assert out[0].key == ("x", "y")
    assert out[0].kind == "changed"
