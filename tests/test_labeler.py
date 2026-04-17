"""Tests for csvdiff.labeler."""
import pytest
from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.labeler import (
    LabelError,
    LabelRule,
    LabelOptions,
    LabeledChange,
    label_diff,
)


def _fc(col: str, old: str, new: str) -> FieldChange:
    return FieldChange(column=col, old_value=old, new_value=new)


def _change(kind: str, key: tuple, old=None, new=None, fields=None) -> RowChange:
    return RowChange(
        kind=kind,
        key=key,
        old_row=old or {},
        new_row=new or {},
        field_changes=fields or [],
    )


def make_result(changes=None) -> DiffResult:
    return DiffResult(changes=changes or [], keys=[])


def _rule(name, col, fn):
    return LabelRule(name=name, column=col, predicate=fn)


def test_label_options_empty_rules_raises():
    with pytest.raises(LabelError):
        LabelOptions(rules=[])


def test_label_options_blank_name_raises():
    with pytest.raises(LabelError):
        LabelOptions(rules=[_rule("  ", "col", lambda v: True)])


def test_label_diff_none_result_raises():
    opts = LabelOptions(rules=[_rule("x", "a", lambda v: True)])
    with pytest.raises(LabelError):
        label_diff(None, opts)


def test_label_diff_none_options_raises():
    with pytest.raises(LabelError):
        label_diff(make_result(), None)


def test_label_diff_empty_result():
    opts = LabelOptions(rules=[_rule("big", "amount", lambda v: int(v or 0) > 100)])
    result = label_diff(make_result(), opts)
    assert result == []


def test_label_diff_matching_rule():
    change = _change("added", ("1",), new={"id": "1", "amount": "200"})
    opts = LabelOptions(rules=[_rule("big", "amount", lambda v: int(v or 0) > 100)])
    out = label_diff(make_result([change]), opts)
    assert len(out) == 1
    assert out[0].labels == ["big"]


def test_label_diff_no_matching_rule():
    change = _change("added", ("1",), new={"id": "1", "amount": "5"})
    opts = LabelOptions(rules=[_rule("big", "amount", lambda v: int(v or 0) > 100)])
    out = label_diff(make_result([change]), opts)
    assert out[0].labels == []


def test_label_diff_multi_false_first_wins():
    change = _change("added", ("1",), new={"status": "urgent"})
    opts = LabelOptions(
        rules=[
            _rule("urgent", "status", lambda v: v == "urgent"),
            _rule("flagged", "status", lambda v: v in ("urgent", "flagged")),
        ],
        multi=False,
    )
    out = label_diff(make_result([change]), opts)
    assert out[0].labels == ["urgent"]


def test_label_diff_multi_true_all_match():
    change = _change("added", ("1",), new={"status": "urgent"})
    opts = LabelOptions(
        rules=[
            _rule("urgent", "status", lambda v: v == "urgent"),
            _rule("flagged", "status", lambda v: v in ("urgent", "flagged")),
        ],
        multi=True,
    )
    out = label_diff(make_result([change]), opts)
    assert set(out[0].labels) == {"urgent", "flagged"}


def test_label_diff_predicate_exception_treated_as_no_match():
    change = _change("added", ("1",), new={"amount": "not-a-number"})
    opts = LabelOptions(rules=[_rule("big", "amount", lambda v: int(v) > 100)])
    out = label_diff(make_result([change]), opts)
    assert out[0].labels == []
