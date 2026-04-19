"""Tests for csvdiff.differ_log."""
from __future__ import annotations

import json
import logging
import pytest

from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.differ_log import (
    LogError,
    LogOptions,
    LogEntry,
    build_log_entry,
    emit_log_entries,
)


def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def make_result(
    added=None, removed=None, changed=None
) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


def test_log_options_default_valid():
    opts = LogOptions()
    assert opts.level == "INFO"
    assert opts.include_stats is True
    assert opts.include_timestamp is True


def test_log_options_invalid_level_raises():
    with pytest.raises(LogError, match="level"):
        LogOptions(level="VERBOSE")


def test_log_options_debug_level_valid():
    opts = LogOptions(level="DEBUG")
    assert opts.level == "DEBUG"


def test_build_log_entry_none_result_raises():
    with pytest.raises(LogError, match="None"):
        build_log_entry(None, "msg")


def test_build_log_entry_blank_message_raises():
    r = make_result()
    with pytest.raises(LogError, match="blank"):
        build_log_entry(r, "   ")


def test_build_log_entry_basic():
    r = make_result(
        added=[{"id": "1"}],
        removed=[{"id": "2"}, {"id": "3"}],
    )
    entry = build_log_entry(r, "diff complete")
    assert entry.level == "INFO"
    assert entry.message == "diff complete"
    assert entry.data["added"] == 1
    assert entry.data["removed"] == 2
    assert entry.data["changed"] == 0
    assert entry.timestamp is not None


def test_build_log_entry_no_stats():
    r = make_result(added=[{"id": "1"}])
    opts = LogOptions(include_stats=False)
    entry = build_log_entry(r, "done", options=opts)
    assert "added" not in entry.data


def test_build_log_entry_no_timestamp():
    r = make_result()
    opts = LogOptions(include_timestamp=False)
    entry = build_log_entry(r, "done", options=opts)
    assert entry.timestamp is None


def test_log_entry_as_dict_includes_timestamp():
    entry = LogEntry(level="INFO", message="hi", data={}, timestamp="2024-01-01T00:00:00+00:00")
    d = entry.as_dict()
    assert d["timestamp"] == "2024-01-01T00:00:00+00:00"


def test_log_entry_as_json_is_valid_json():
    r = make_result(added=[{"id": "1"}])
    entry = build_log_entry(r, "test")
    parsed = json.loads(entry.as_json())
    assert parsed["message"] == "test"
    assert parsed["data"]["added"] == 1


def test_emit_log_entries_calls_logger(caplog):
    r = make_result(added=[{"id": "x"}])
    entry = build_log_entry(r, "emitting")
    with caplog.at_level(logging.INFO, logger="csvdiff"):
        emit_log_entries([entry])
    assert any("emitting" in rec.message for rec in caplog.records)


def test_emit_log_entries_empty_list_no_error():
    emit_log_entries([])
