"""Tests for csvdiff.scorer2."""
import pytest

from csvdiff.differ import DiffResult, FieldChange, RowChange
from csvdiff.scorer2 import (
    WeightError,
    WeightOptions,
    ScoredChange,
    score_changes,
    top_changes,
)


def _fc(field: str, old: str = "a", new: str = "b") -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(
    key=("1",),
    field_changes=None,
    added_row=None,
    removed_row=None,
) -> RowChange:
    return RowChange(
        key=key,
        field_changes=field_changes or [],
        added_row=added_row,
        removed_row=removed_row,
    )


def make_result(changes=None) -> DiffResult:
    return DiffResult(changes=changes or [])


def test_weight_options_defaults_are_safe():
    opts = WeightOptions()
    assert opts.default_weight == 1.0
    assert opts.missing_penalty == 0.0


def test_weight_options_negative_default_raises():
    with pytest.raises(WeightError):
        WeightOptions(default_weight=-1.0)


def test_weight_options_negative_column_weight_raises():
    with pytest.raises(WeightError):
        WeightOptions(weights={"col": -0.5})


def test_score_changes_none_raises():
    with pytest.raises(WeightError):
        score_changes(None)


def test_score_changes_empty_result():
    result = make_result()
    scored = score_changes(result)
    assert scored == []


def test_score_changes_default_weight():
    c = _change(field_changes=[_fc("name"), _fc("age")])
    scored = score_changes(make_result([c]))
    assert len(scored) == 1
    assert scored[0].score == pytest.approx(2.0)


def test_score_changes_custom_weights():
    opts = WeightOptions(weights={"name": 3.0}, default_weight=1.0)
    c = _change(field_changes=[_fc("name"), _fc("age")])
    scored = score_changes(make_result([c]), opts)
    assert scored[0].score == pytest.approx(4.0)


def test_score_added_row_uses_missing_penalty():
    opts = WeightOptions(missing_penalty=5.0)
    c = _change(added_row={"id": "1"})
    scored = score_changes(make_result([c]), opts)
    assert scored[0].score == pytest.approx(5.0)


def test_score_removed_row_uses_missing_penalty():
    opts = WeightOptions(missing_penalty=2.0)
    c = _change(removed_row={"id": "1"})
    scored = score_changes(make_result([c]), opts)
    assert scored[0].score == pytest.approx(2.0)


def test_top_changes_returns_sorted():
    c1 = _change(key=("1",), field_changes=[_fc("a")])
    c2 = _change(key=("2",), field_changes=[_fc("a"), _fc("b")])
    c3 = _change(key=("3",), field_changes=[_fc("a"), _fc("b"), _fc("c")])
    scored = score_changes(make_result([c1, c2, c3]))
    top = top_changes(scored, n=2)
    assert len(top) == 2
    assert top[0].score >= top[1].score
    assert top[0].change.key == ("3",)


def test_top_changes_negative_n_raises():
    with pytest.raises(WeightError):
        top_changes([], n=-1)


def test_top_changes_n_larger_than_list():
    c = _change(field_changes=[_fc("x")])
    scored = score_changes(make_result([c]))
    top = top_changes(scored, n=100)
    assert len(top) == 1
