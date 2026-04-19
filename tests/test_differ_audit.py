"""Tests for csvdiff.differ_audit."""
import os
import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_audit import (
    AuditError,
    AuditEntry,
    build_entry,
    append_audit_log,
    load_audit_log,
)


def _make_result(added=0, removed=0, changed=0) -> DiffResult:
    def _rows(n):
        return [RowChange(key=(str(i),), old={}, new={"x": str(i)}) for i in range(n)]
    return DiffResult(
        added=_rows(added),
        removed=_rows(removed),
        changed=_rows(changed),
    )


def test_build_entry_basic():
    result = _make_result(added=2, removed=1, changed=3)
    entry = build_entry(result, "a.csv", "b.csv", ["id"])
    assert entry.added == 2
    assert entry.removed == 1
    assert entry.changed == 3
    assert entry.file_a == "a.csv"
    assert entry.file_b == "b.csv"
    assert entry.key_columns == ["id"]
    assert entry.note is None
    assert entry.timestamp.endswith("Z")


def test_build_entry_with_note():
    result = _make_result()
    entry = build_entry(result, "a.csv", "b.csv", ["id"], note="nightly run")
    assert entry.note == "nightly run"


def test_build_entry_none_result_raises():
    with pytest.raises(AuditError, match="result"):
        build_entry(None, "a.csv", "b.csv", ["id"])


def test_build_entry_empty_file_a_raises():
    with pytest.raises(AuditError, match="file paths"):
        build_entry(_make_result(), "", "b.csv", ["id"])


def test_build_entry_empty_file_b_raises():
    with pytest.raises(AuditError, match="file paths"):
        build_entry(_make_result(), "a.csv", "", ["id"])


def test_build_entry_empty_keys_raises():
    with pytest.raises(AuditError, match="key_columns"):
        build_entry(_make_result(), "a.csv", "b.csv", [])


def test_as_dict_has_expected_keys():
    result = _make_result(added=1)
    entry = build_entry(result, "a.csv", "b.csv", ["id"])
    d = entry.as_dict()
    for k in ("timestamp", "user", "host", "file_a", "file_b", "key_columns", "added", "removed", "changed"):
        assert k in d


def test_append_and_load_roundtrip(tmp_path):
    log = str(tmp_path / "audit.log")
    r1 = _make_result(added=1)
    r2 = _make_result(removed=2, changed=1)
    e1 = build_entry(r1, "a.csv", "b.csv", ["id"])
    e2 = build_entry(r2, "c.csv", "d.csv", ["id", "name"], note="test")
    append_audit_log(e1, log)
    append_audit_log(e2, log)
    entries = load_audit_log(log)
    assert len(entries) == 2
    assert entries[0].added == 1
    assert entries[1].removed == 2
    assert entries[1].note == "test"
    assert entries[1].key_columns == ["id", "name"]


def test_append_none_entry_raises(tmp_path):
    log = str(tmp_path / "audit.log")
    with pytest.raises(AuditError, match="entry"):
        append_audit_log(None, log)


def test_append_blank_path_raises():
    entry = build_entry(_make_result(), "a.csv", "b.csv", ["id"])
    with pytest.raises(AuditError, match="path"):
        append_audit_log(entry, "   ")


def test_load_blank_path_raises():
    with pytest.raises(AuditError, match="path"):
        load_audit_log("")
