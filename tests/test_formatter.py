"""Tests for csvdiff.formatter module."""

import json
import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.formatter import format_diff


def make_result(
    added=None, removed=None, changed=None
) -> DiffResult:
    """Create a DiffResult with optional added, removed, and changed entries."""
    return DiffResult(
        added=added or {},
        removed=removed or {},
        changed=changed or {},
    )


def test_format_text_no_differences():
    result = make_result()
    output = format_diff(result, fmt="text")
    assert "No differences found" in output


def test_format_text_added_row():
    result = make_result(added={("1",): {"id": "1", "name": "Alice"}})
    output = format_diff(result, fmt="text")
    assert output.startswith("+")
    assert "1" in output


def test_format_text_removed_row():
    result = make_result(removed={("2",): {"id": "2", "name": "Bob"}})
    output = format_diff(result, fmt="text")
    assert output.startswith("-")
    assert "2" in output


def test_format_text_changed_row():
    change = RowChange(field_changes={"name": ("Bob", "Robert")})
    result = make_result(changed={("2",): change})
    output = format_diff(result, fmt="text")
    assert "~" in output
    assert "name" in output
    assert "Bob" in output
    assert "Robert" in output


def test_format_json_structure():
    change = RowChange(field_changes={"score": ("10", "20")})
    result = make_result(
        added={("3",): {"id": "3", "score": "99"}},
        removed={("4",): {"id": "4", "score": "0"}},
        changed={("5",): change},
    )
    output = format_diff(result, fmt="json")
    data = json.loads(output)
    assert "added" in data
    assert "removed" in data
    assert "changed" in data
    assert "3" in data["added"]
    assert "4" in data["removed"]
    assert "5" in data["changed"]
    assert data["changed"]["5"]["field_changes"]["score"]["old"] == "10"
    assert data["changed"]["5"]["field_changes"]["score"]["new"] == "20"


def test_format_json_no_differences():
    """JSON output for an empty diff should still contain the expected keys."""
    result = make_result()
    output = format_diff(result, fmt="json")
    data = json.loads(output)
    assert data["added"] == {}
    assert data["removed"] == {}
    assert data["changed"] == {}


def test_format_csv_added_row():
    result = make_result(added={("1",): {"id": "1", "name": "Alice"}})
    output = format_diff(result, fmt="csv")
    assert "_diff" in output
    assert "added" in output
    assert "Alice" in output


def test_format_csv_empty_diff():
    result = make_result()
    output = format_diff(result, fmt="csv")
    assert output == ""


def test_format_default_is_text():
    result = make_result()
    output_default = format_diff(result)
    output_text = format_diff(result, fmt="text")
    assert output_default == output_text


def test_format_invalid_fmt_raises():
    """format_diff should raise ValueError for unsupported format strings."""
    result = make_result()
    with pytest.raises(ValueError, match="unsupported format"):
        format_diff(result, fmt="xml")
