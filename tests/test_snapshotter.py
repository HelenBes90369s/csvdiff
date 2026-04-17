"""Tests for csvdiff.snapshotter."""
from __future__ import annotations

import pathlib
import pytest

from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.snapshotter import (
    SnapshotError,
    SnapshotMeta,
    load_snapshot,
    save_snapshot,
    snapshot_exists,
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


# ---------------------------------------------------------------------------
# save_snapshot
# ---------------------------------------------------------------------------

def test_save_snapshot_none_raises():
    with pytest.raises(SnapshotError):
        save_snapshot(None, "/tmp/x.json")  # type: ignore


def test_save_snapshot_returns_meta(tmp_path):
    dest = tmp_path / "snap.json"
    result = make_result()
    meta = save_snapshot(result, dest)
    assert isinstance(meta, SnapshotMeta)
    assert meta.path == dest
    assert meta.size_bytes > 0


def test_save_snapshot_creates_file(tmp_path):
    dest = tmp_path / "snap.json"
    save_snapshot(make_result(), dest)
    assert dest.exists()


def test_save_snapshot_content_is_valid_json(tmp_path):
    import json
    dest = tmp_path / "snap.json"
    save_snapshot(make_result(added=[{"id": "1", "name": "Alice"}]), dest)
    data = json.loads(dest.read_text())
    assert "added" in data


# ---------------------------------------------------------------------------
# load_snapshot
# ---------------------------------------------------------------------------

def test_load_snapshot_missing_file_raises(tmp_path):
    with pytest.raises(SnapshotError, match="not found"):
        load_snapshot(tmp_path / "missing.json")


def test_load_snapshot_roundtrip_empty(tmp_path):
    dest = tmp_path / "snap.json"
    original = make_result()
    save_snapshot(original, dest)
    restored = load_snapshot(dest)
    assert restored.added == []
    assert restored.removed == []
    assert restored.changed == []


def test_load_snapshot_roundtrip_added_row(tmp_path):
    dest = tmp_path / "snap.json"
    original = make_result(added=[{"id": "1", "val": "x"}])
    save_snapshot(original, dest)
    restored = load_snapshot(dest)
    assert restored.added == [{"id": "1", "val": "x"}]


def test_load_snapshot_roundtrip_changed_row(tmp_path):
    dest = tmp_path / "snap.json"
    change = RowChange(
        key=("1",),
        field_changes=[_fc("name", "Alice", "Bob")],
    )
    original = make_result(changed=[change])
    save_snapshot(original, dest)
    restored = load_snapshot(dest)
    assert len(restored.changed) == 1
    assert restored.changed[0].key == ("1",)


# ---------------------------------------------------------------------------
# snapshot_exists
# ---------------------------------------------------------------------------

def test_snapshot_exists_false_when_missing(tmp_path):
    assert snapshot_exists(tmp_path / "no.json") is False


def test_snapshot_exists_true_after_save(tmp_path):
    dest = tmp_path / "snap.json"
    save_snapshot(make_result(), dest)
    assert snapshot_exists(dest) is True
