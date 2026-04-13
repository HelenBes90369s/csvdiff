"""Tests for csvdiff.highlighter."""

from __future__ import annotations

import pytest

from csvdiff.differ import FieldChange, RowChange
from csvdiff.highlighter import (
    HighlightedField,
    HighlightError,
    highlight_diff,
    highlight_row_change,
)


def _fc(field: str, old: str | None, new: str | None) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key: tuple, *field_changes: FieldChange) -> RowChange:
    return RowChange(key=key, field_changes=list(field_changes))


# ---------------------------------------------------------------------------
# HighlightedField.render
# ---------------------------------------------------------------------------

def test_highlighted_field_render_no_colour_change():
    hf = HighlightedField(field="age", old_value="30", new_value="31", colour="")
    result = hf.render(colour=False)
    assert result == "age: '30' -> '31'"


def test_highlighted_field_render_no_colour_added():
    hf = HighlightedField(field="email", old_value=None, new_value="a@b.com", colour="")
    result = hf.render(colour=False)
    assert result == "email: 'a@b.com'"


def test_highlighted_field_render_no_colour_removed():
    hf = HighlightedField(field="email", old_value="a@b.com", new_value=None, colour="")
    result = hf.render(colour=False)
    assert result == "email: 'a@b.com'"


def test_highlighted_field_render_with_colour_contains_field_name():
    hf = HighlightedField(field="name", old_value="Alice", new_value="Bob", colour="\033[33m")
    result = hf.render(colour=True)
    assert "name" in result
    assert "Alice" in result
    assert "Bob" in result
    assert "\033[" in result  # some ANSI code present


# ---------------------------------------------------------------------------
# highlight_row_change
# ---------------------------------------------------------------------------

def test_highlight_row_change_returns_one_line_per_field():
    change = _change(("1",), _fc("name", "Alice", "Bob"), _fc("age", "30", "31"))
    lines = highlight_row_change(change, colour=False)
    assert len(lines) == 2
    assert "name" in lines[0]
    assert "age" in lines[1]


def test_highlight_row_change_empty_fields():
    change = _change(("1",))
    lines = highlight_row_change(change, colour=False)
    assert lines == []


# ---------------------------------------------------------------------------
# highlight_diff
# ---------------------------------------------------------------------------

def test_highlight_diff_no_changes():
    result = highlight_diff([], colour=False)
    assert result == "No differences found."


def test_highlight_diff_single_change_no_colour():
    change = _change(("id-1",), _fc("status", "active", "inactive"))
    result = highlight_diff([change], colour=False)
    assert "Row id-1" in result
    assert "status" in result
    assert "active" in result
    assert "inactive" in result


def test_highlight_diff_respects_max_rows():
    changes = [_change((str(i),), _fc("v", str(i), str(i + 1))) for i in range(5)]
    result = highlight_diff(changes, colour=False, max_rows=2)
    assert "Row 0" in result
    assert "Row 1" in result
    assert "Row 4" not in result
    assert "3 more row(s)" in result


def test_highlight_diff_max_rows_exact_count_no_truncation_message():
    changes = [_change((str(i),), _fc("v", str(i), str(i + 1))) for i in range(3)]
    result = highlight_diff(changes, colour=False, max_rows=3)
    assert "more row" not in result


def test_highlight_diff_composite_key():
    change = _change(("Alice", "2024"), _fc("score", "88", "92"))
    result = highlight_diff([change], colour=False)
    assert "Alice, 2024" in result
