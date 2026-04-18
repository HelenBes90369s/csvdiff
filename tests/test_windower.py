"""Tests for csvdiff.windower."""
import pytest
from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.windower import (
    WindowError,
    WindowOptions,
    DiffWindow,
    window_diff,
    total_windows,
)


def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key: tuple, kind: str = "changed") -> RowChange:
    fc = _fc("col", "a", "b")
    return RowChange(key=key, kind=kind, field_changes=[fc], old_row={}, new_row={})


def make_result(added=(), removed=(), changed=()) -> DiffResult:
    return DiffResult(added=list(added), removed=list(removed), changed=list(changed))


def test_window_options_default_is_valid():
    opts = WindowOptions()
    assert opts.size == 10
    assert opts.step == 1


def test_window_options_zero_size_raises():
    with pytest.raises(WindowError):
        WindowOptions(size=0)


def test_window_options_zero_step_raises():
    with pytest.raises(WindowError):
        WindowOptions(step=0)


def test_window_options_negative_raises():
    with pytest.raises(WindowError):
        WindowOptions(size=-1)


def test_window_diff_none_raises():
    with pytest.raises(WindowError):
        window_diff(None)


def test_window_diff_empty_result_returns_one_empty_window():
    result = make_result()
    windows = window_diff(result)
    assert len(windows) == 1
    assert windows[0].is_empty


def test_window_diff_single_window():
    changes = [_change((str(i),)) for i in range(3)]
    result = make_result(changed=changes)
    opts = WindowOptions(size=10, step=1)
    windows = window_diff(result, opts)
    assert len(windows) == 1
    assert len(windows[0].changes) == 3


def test_window_diff_multiple_windows():
    changes = [_change((str(i),)) for i in range(5)]
    result = make_result(changed=changes)
    opts = WindowOptions(size=3, step=3)
    windows = window_diff(result, opts)
    assert len(windows) == 2
    assert len(windows[0].changes) == 3
    assert len(windows[1].changes) == 2


def test_window_diff_overlapping():
    changes = [_change((str(i),)) for i in range(4)]
    result = make_result(changed=changes)
    opts = WindowOptions(size=3, step=1)
    windows = window_diff(result, opts)
    assert len(windows) == 4
    assert windows[0].changes[0].key == ("0",)
    assert windows[1].changes[0].key == ("1",)


def test_window_index_increments():
    changes = [_change((str(i),)) for i in range(6)]
    result = make_result(changed=changes)
    opts = WindowOptions(size=2, step=2)
    windows = window_diff(result, opts)
    for i, w in enumerate(windows):
        assert w.index == i


def test_total_windows_matches_list_length():
    changes = [_change((str(i),)) for i in range(7)]
    result = make_result(changed=changes)
    opts = WindowOptions(size=3, step=2)
    assert total_windows(result, opts) == len(window_diff(result, opts))


def test_window_diff_combines_all_kinds():
    result = make_result(
        added=[_change(("a",), "added")],
        removed=[_change(("b",), "removed")],
        changed=[_change(("c",), "changed")],
    )
    opts = WindowOptions(size=10)
    windows = window_diff(result, opts)
    assert len(windows[0].changes) == 3
