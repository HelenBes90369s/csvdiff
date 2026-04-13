"""Tests for csvdiff.exporter."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.exporter import ExportError, export_diff


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fc(field: str, old: str, new: str):
    from csvdiff.differ import FieldChange
    return FieldChange(field=field, old_value=old, new_value=new)


def make_result() -> DiffResult:
    return DiffResult(
        added=[{"id": "3", "name": "Carol"}],
        removed=[{"id": "2", "name": "Bob"}],
        changed=[
            RowChange(
                key=("1",),
                old_row={"id": "1", "name": "Alice"},
                new_row={"id": "1", "name": "Alicia"},
                changes=[_fc("name", "Alice", "Alicia")],
            )
        ],
    )


# ---------------------------------------------------------------------------
# JSON export
# ---------------------------------------------------------------------------

def test_export_json_structure(tmp_path: Path) -> None:
    out = tmp_path / "diff.json"
    export_diff(make_result(), out, fmt="json")
    data = json.loads(out.read_text())
    assert "added" in data
    assert "removed" in data
    assert "changed" in data
    assert data["added"] == [{"id": "3", "name": "Carol"}]
    assert data["removed"] == [{"id": "2", "name": "Bob"}]
    assert len(data["changed"]) == 1
    assert data["changed"][0]["fields"][0]["name"] == "name"


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------

def test_export_csv_has_header(tmp_path: Path) -> None:
    out = tmp_path / "diff.csv"
    export_diff(make_result(), out, fmt="csv", key_columns=["id"])
    rows = list(csv.reader(out.read_text().splitlines()))
    assert rows[0][0] == "change_type"
    assert "field" in rows[0]


def test_export_csv_changed_row_recorded(tmp_path: Path) -> None:
    out = tmp_path / "diff.csv"
    export_diff(make_result(), out, fmt="csv", key_columns=["id"])
    rows = list(csv.DictReader(out.read_text().splitlines()))
    changed = [r for r in rows if r["change_type"] == "changed"]
    assert len(changed) == 1
    assert changed[0]["field"] == "name"
    assert changed[0]["old_value"] == "Alice"
    assert changed[0]["new_value"] == "Alicia"


# ---------------------------------------------------------------------------
# Text export
# ---------------------------------------------------------------------------

def test_export_text_writes_file(tmp_path: Path) -> None:
    out = tmp_path / "diff.txt"
    export_diff(make_result(), out, fmt="text")
    content = out.read_text()
    assert len(content) > 0


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_export_unsupported_format_raises(tmp_path: Path) -> None:
    with pytest.raises(ExportError, match="Unsupported export format"):
        export_diff(make_result(), tmp_path / "out.xml", fmt="xml")


def test_export_bad_path_raises() -> None:
    with pytest.raises(ExportError, match="Could not write"):
        export_diff(make_result(), "/no/such/directory/out.json", fmt="json")
