"""Tests for csvdiff.differ_cursor."""
import pytest

from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.differ_cursor import (
    CursorError,
    CursorOptions,
    CursorState,
    iter_cursor,
)


def _fc(field: str = "col", old: str = "a", new: str = "b") -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key: tuple = ("1",), kind: str = "changed") -> RowChange:
    return RowChange(
        key=key,
        kind=kind,
        row={"id": key[0]},
        field_changes=[_fc()] if kind == "changed" else [],
    )


def make_result(
    added=None, removed=None, changed=None
) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


# --- CursorOptions ---

def test_options_default_valid():
    opts = CursorOptions()
    assert opts.page_size == 50
    assert opts.start == 0


def test_options_zero_page_size_raises():
    with pytest.raises(CursorError, match="page_size"):
        CursorOptions(page_size=0)


def test_options_negative_page_size_raises():
    with pytest.raises(CursorError, match="page_size"):
        CursorOptions(page_size=-1)


def test_options_negative_start_raises():
    with pytest.raises(CursorError, match="start"):
        CursorOptions(start=-1)


# --- CursorState ---

def test_cursor_state_load_none_raises():
    state = CursorState(options=CursorOptions())
    with pytest.raises(CursorError, match="None"):
        state.load(None)  # type: ignore[arg-type]


def test_cursor_state_exhausted_on_empty():
    state = CursorState(options=CursorOptions())
    state.load(make_result())
    assert state.exhausted


def test_cursor_state_next_page_returns_items():
    changes = [_change((str(i),)) for i in range(5)]
    state = CursorState(options=CursorOptions(page_size=3))
    state.load(make_result(changed=changes))
    page = state.next_page()
    assert len(page) == 3
    assert state.position == 3


def test_cursor_state_next_page_last_partial():
    changes = [_change((str(i),)) for i in range(5)]
    state = CursorState(options=CursorOptions(page_size=3))
    state.load(make_result(changed=changes))
    state.next_page()  # consume first 3
    page = state.next_page()
    assert len(page) == 2
    assert state.exhausted


def test_cursor_state_next_page_when_exhausted_returns_empty():
    state = CursorState(options=CursorOptions())
    state.load(make_result())
    assert state.next_page() == []


def test_cursor_state_reset():
    changes = [_change((str(i),)) for i in range(4)]
    state = CursorState(options=CursorOptions(page_size=4))
    state.load(make_result(changed=changes))
    state.next_page()
    assert state.exhausted
    state.reset()
    assert not state.exhausted
    assert state.position == 0


def test_cursor_state_start_offset():
    changes = [_change((str(i),)) for i in range(10)]
    state = CursorState(options=CursorOptions(page_size=3, start=5))
    state.load(make_result(changed=changes))
    page = state.next_page()
    assert len(page) == 3
    assert page[0].key == ("5",)


# --- iter_cursor ---

def test_iter_cursor_none_raises():
    with pytest.raises(CursorError, match="None"):
        list(iter_cursor(None))  # type: ignore[arg-type]


def test_iter_cursor_empty_yields_nothing():
    pages = list(iter_cursor(make_result()))
    assert pages == []


def test_iter_cursor_collects_all_changes():
    added = [_change(("a",), kind="added")]
    removed = [_change(("b",), kind="removed")]
    changed = [_change(("c",))]
    result = make_result(added=added, removed=removed, changed=changed)
    all_items = [item for page in iter_cursor(result, CursorOptions(page_size=2)) for item in page]
    assert len(all_items) == 3


def test_iter_cursor_page_count():
    changes = [_change((str(i),)) for i in range(7)]
    pages = list(iter_cursor(make_result(changed=changes), CursorOptions(page_size=3)))
    assert len(pages) == 3
    assert len(pages[0]) == 3
    assert len(pages[1]) == 3
    assert len(pages[2]) == 1
