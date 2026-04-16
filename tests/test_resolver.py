"""Tests for csvdiff.resolver."""
import pytest
from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.resolver import ResolveError, ResolveOptions, resolve_diff


def _fc(field="name", old="a", new="b"):
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key=("1",), **kwargs):
    return RowChange(key=key, field_changes=[_fc(**kwargs)])


def make_result(added=(), removed=(), changed=()):
    return DiffResult(added=list(added), removed=list(removed), changed=list(changed))


def test_options_default_is_left():
    opts = ResolveOptions()
    assert opts.strategy == "left"


def test_options_invalid_strategy_raises():
    with pytest.raises(ResolveError):
        ResolveOptions(strategy="bad")


def test_resolve_none_raises():
    with pytest.raises(ResolveError):
        resolve_diff(None, make_result())


def test_resolve_left_strategy_keeps_left():
    left = make_result(added=[_change(("1",), old="x", new="y")])
    right = make_result(added=[_change(("1",), old="p", new="q")])
    result = resolve_diff(left, right, ResolveOptions(strategy="left"))
    assert result.added[0].field_changes[0].old_value == "x"


def test_resolve_right_strategy_keeps_right():
    left = make_result(added=[_change(("1",), old="x", new="y")])
    right = make_result(added=[_change(("1",), old="p", new="q")])
    result = resolve_diff(left, right, ResolveOptions(strategy="right"))
    assert result.added[0].field_changes[0].old_value == "p"


def test_resolve_union_includes_all_keys():
    left = make_result(changed=[_change(("1",)), _change(("2",))])
    right = make_result(changed=[_change(("3",))])
    result = resolve_diff(left, right, ResolveOptions(strategy="union"))
    keys = {c.key for c in result.changed}
    assert keys == {("1",), ("2",), ("3",)}


def test_resolve_union_left_wins_on_conflict():
    left = make_result(changed=[_change(("1",), old="L", new="L2")])
    right = make_result(changed=[_change(("1",), old="R", new="R2")])
    result = resolve_diff(left, right, ResolveOptions(strategy="union"))
    assert result.changed[0].field_changes[0].old_value == "L"


def test_resolve_intersection_keeps_common_only():
    left = make_result(removed=[_change(("1",)), _change(("2",))])
    right = make_result(removed=[_change(("2",)), _change(("3",))])
    result = resolve_diff(left, right, ResolveOptions(strategy="intersection"))
    assert len(result.removed) == 1
    assert result.removed[0].key == ("2",)


def test_resolve_intersection_empty_when_no_overlap():
    left = make_result(added=[_change(("1",))])
    right = make_result(added=[_change(("2",))])
    result = resolve_diff(left, right, ResolveOptions(strategy="intersection"))
    assert result.added == []


def test_resolve_empty_results():
    result = resolve_diff(make_result(), make_result())
    assert result.added == []
    assert result.removed == []
    assert result.changed == []
