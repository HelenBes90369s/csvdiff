"""Tests for csvdiff.differ_patch."""
import pytest
from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.differ_patch import (
    PatchError, PatchOp, Patch, build_patch, apply_patch, invert_patch
)


def _fc(field, old, new):
    return FieldChange(field=field, old_value=old, new_value=new)


def make_result(added=None, removed=None, changed=None):
    return DiffResult(
        added=added or {},
        removed=removed or {},
        changed=changed or {},
    )


def test_build_patch_none_raises():
    with pytest.raises(PatchError):
        build_patch(None)


def test_build_patch_empty():
    patch = build_patch(make_result())
    assert len(patch) == 0


def test_build_patch_added_row():
    result = make_result(added={("1",): {"id": "1", "name": "Alice"}})
    patch = build_patch(result)
    assert len(patch) == 1
    op = patch.ops[0]
    assert op.op == "add"
    assert op.key == ("1",)
    assert op.new == {"id": "1", "name": "Alice"}


def test_build_patch_removed_row():
    result = make_result(removed={("2",): {"id": "2", "name": "Bob"}})
    patch = build_patch(result)
    assert len(patch) == 1
    op = patch.ops[0]
    assert op.op == "remove"
    assert op.old == {"id": "2", "name": "Bob"}


def test_build_patch_changed_row():
    change = RowChange(
        key=("3",),
        old_row={"id": "3", "val": "x"},
        new_row={"id": "3", "val": "y"},
        field_changes=[_fc("val", "x", "y")],
    )
    result = make_result(changed={("3",): change})
    patch = build_patch(result)
    assert len(patch) == 1
    op = patch.ops[0]
    assert op.op == "replace"


def test_apply_patch_add():
    rows = {}
    patch = Patch(ops=[PatchOp(op="add", key=("1",), new={"id": "1"})])
    out = apply_patch(rows, patch)
    assert out[("1",)] == {"id": "1"}


def test_apply_patch_remove():
    rows = {("1",): {"id": "1"}}
    patch = Patch(ops=[PatchOp(op="remove", key=("1",), old={"id": "1"})])
    out = apply_patch(rows, patch)
    assert ("1",) not in out


def test_apply_patch_replace():
    rows = {("1",): {"id": "1", "v": "a"}}
    patch = Patch(ops=[PatchOp(op="replace", key=("1",), old={"id": "1", "v": "a"}, new={"id": "1", "v": "b"})])
    out = apply_patch(rows, patch)
    assert out[("1",)]["v"] == "b"


def test_apply_patch_unknown_op_raises():
    rows = {}
    patch = Patch(ops=[PatchOp(op="upsert", key=("1",))])
    with pytest.raises(PatchError):
        apply_patch(rows, patch)


def test_apply_patch_none_raises():
    with pytest.raises(PatchError):
        apply_patch({}, None)


def test_invert_patch_add_becomes_remove():
    patch = Patch(ops=[PatchOp(op="add", key=("1",), new={"id": "1"})])
    inv = invert_patch(patch)
    assert inv.ops[0].op == "remove"


def test_invert_patch_remove_becomes_add():
    patch = Patch(ops=[PatchOp(op="remove", key=("1",), old={"id": "1"})])
    inv = invert_patch(patch)
    assert inv.ops[0].op == "add"
    assert inv.ops[0].new == {"id": "1"}


def test_invert_patch_replace_swaps_old_new():
    patch = Patch(ops=[PatchOp(op="replace", key=("1",), old={"v": "a"}, new={"v": "b"})])
    inv = invert_patch(patch)
    op = inv.ops[0]
    assert op.old == {"v": "b"}
    assert op.new == {"v": "a"}


def test_invert_none_raises():
    with pytest.raises(PatchError):
        invert_patch(None)


def test_roundtrip_apply_invert():
    rows = {("1",): {"id": "1", "v": "a"}}
    patch = Patch(ops=[PatchOp(op="replace", key=("1",), old={"id": "1", "v": "a"}, new={"id": "1", "v": "b"})])
    patched = apply_patch(rows, patch)
    restored = apply_patch(patched, invert_patch(patch))
    assert restored == rows
