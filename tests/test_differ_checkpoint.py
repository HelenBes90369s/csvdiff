"""Tests for csvdiff.differ_checkpoint."""
from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.differ_checkpoint import (
    CheckpointError,
    CheckpointOptions,
    save_checkpoint,
    load_checkpoint,
    checkpoint_exists,
    delete_checkpoint,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

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


def _change(key: tuple, fields=None) -> RowChange:
    return RowChange(key=key, field_changes=fields or [])


# ---------------------------------------------------------------------------
# CheckpointOptions
# ---------------------------------------------------------------------------

def test_options_blank_dir_raises():
    with pytest.raises(CheckpointError, match="directory"):
        CheckpointOptions(directory="   ")


def test_options_blank_prefix_raises():
    with pytest.raises(CheckpointError, match="prefix"):
        CheckpointOptions(directory="/tmp", prefix="")


def test_options_defaults_are_valid():
    opts = CheckpointOptions(directory="/tmp")
    assert opts.prefix == "csvdiff_checkpoint"


# ---------------------------------------------------------------------------
# save / load round-trip
# ---------------------------------------------------------------------------

def test_save_returns_meta(tmp_path):
    opts = CheckpointOptions(directory=str(tmp_path))
    result = make_result()
    meta = save_checkpoint(result, opts, label="step1")
    assert meta.label == "step1"
    assert meta.size_bytes > 0


def test_save_creates_file(tmp_path):
    opts = CheckpointOptions(directory=str(tmp_path))
    meta = save_checkpoint(make_result(), opts, label="step2")
    import pathlib
    assert pathlib.Path(meta.path).exists()


def test_roundtrip_empty_result(tmp_path):
    opts = CheckpointOptions(directory=str(tmp_path))
    original = make_result()
    save_checkpoint(original, opts, label="empty")
    restored = load_checkpoint(opts, label="empty")
    assert restored.added == [] and restored.removed == [] and restored.changed == []


def test_roundtrip_with_changes(tmp_path):
    opts = CheckpointOptions(directory=str(tmp_path))
    change = _change(("id1",), fields=[_fc("name", "Alice", "Bob")])
    original = make_result(changed=[change])
    save_checkpoint(original, opts, label="with_changes")
    restored = load_checkpoint(opts, label="with_changes")
    assert len(restored.changed) == 1
    assert restored.changed[0].key == ("id1",)


def test_save_none_result_raises(tmp_path):
    opts = CheckpointOptions(directory=str(tmp_path))
    with pytest.raises(CheckpointError, match="None"):
        save_checkpoint(None, opts, label="x")  # type: ignore[arg-type]


def test_save_blank_label_raises(tmp_path):
    opts = CheckpointOptions(directory=str(tmp_path))
    with pytest.raises(CheckpointError, match="label"):
        save_checkpoint(make_result(), opts, label="  ")


# ---------------------------------------------------------------------------
# checkpoint_exists / delete_checkpoint
# ---------------------------------------------------------------------------

def test_checkpoint_exists_false_before_save(tmp_path):
    opts = CheckpointOptions(directory=str(tmp_path))
    assert checkpoint_exists(opts, "missing") is False


def test_checkpoint_exists_true_after_save(tmp_path):
    opts = CheckpointOptions(directory=str(tmp_path))
    save_checkpoint(make_result(), opts, label="exists_test")
    assert checkpoint_exists(opts, "exists_test") is True


def test_delete_returns_true_when_existed(tmp_path):
    opts = CheckpointOptions(directory=str(tmp_path))
    save_checkpoint(make_result(), opts, label="to_delete")
    assert delete_checkpoint(opts, "to_delete") is True
    assert not checkpoint_exists(opts, "to_delete")


def test_delete_returns_false_when_missing(tmp_path):
    opts = CheckpointOptions(directory=str(tmp_path))
    assert delete_checkpoint(opts, "ghost") is False


def test_load_missing_checkpoint_raises(tmp_path):
    opts = CheckpointOptions(directory=str(tmp_path))
    with pytest.raises(CheckpointError, match="not found"):
        load_checkpoint(opts, label="nonexistent")
