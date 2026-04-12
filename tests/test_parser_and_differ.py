"""Tests for csvdiff parser and differ modules."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from csvdiff.parser import CSVParseError, index_rows, read_csv
from csvdiff.differ import diff_csv


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def write_csv(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# parser tests
# ---------------------------------------------------------------------------

def test_read_csv_basic(tmp_path):
    p = write_csv(tmp_path, "a.csv", """\
        id,name,score
        1,Alice,90
        2,Bob,85
    """)
    headers, rows = read_csv(p)
    assert headers == ["id", "name", "score"]
    assert len(rows) == 2
    assert rows[0] == {"id": "1", "name": "Alice", "score": "90"}


def test_read_csv_missing_file():
    with pytest.raises(CSVParseError, match="File not found"):
        read_csv("/nonexistent/path/file.csv")


def test_index_rows_composite_key():
    rows = [
        {"a": "1", "b": "x", "val": "foo"},
        {"a": "2", "b": "y", "val": "bar"},
    ]
    index = index_rows(rows, ["a", "b"])
    assert ("1", "x") in index
    assert index[("2", "y")]["val"] == "bar"


def test_index_rows_duplicate_key_raises():
    rows = [
        {"id": "1", "val": "a"},
        {"id": "1", "val": "b"},
    ]
    with pytest.raises(CSVParseError, match="Duplicate key"):
        index_rows(rows, ["id"])


def test_index_rows_missing_key_column_raises():
    rows = [{"id": "1", "val": "a"}]
    with pytest.raises(CSVParseError, match="Key column"):
        index_rows(rows, ["nonexistent"])


# ---------------------------------------------------------------------------
# differ tests
# ---------------------------------------------------------------------------

def test_diff_added():
    old = [{"id": "1", "name": "Alice"}]
    new = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
    result = diff_csv(old, new, ["id"])
    assert len(result.added) == 1
    assert result.added[0].key == ("2",)
    assert not result.removed
    assert not result.modified


def test_diff_removed():
    old = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
    new = [{"id": "1", "name": "Alice"}]
    result = diff_csv(old, new, ["id"])
    assert len(result.removed) == 1
    assert result.removed[0].key == ("2",)


def test_diff_modified():
    old = [{"id": "1", "name": "Alice", "score": "90"}]
    new = [{"id": "1", "name": "Alice", "score": "95"}]
    result = diff_csv(old, new, ["id"])
    assert len(result.modified) == 1
    change = result.modified[0]
    assert change.diff == {"score": ("90", "95")}


def test_diff_no_changes():
    rows = [{"id": "1", "name": "Alice"}]
    result = diff_csv(rows, rows, ["id"])
    assert not result.has_changes
    assert result.total == 0
