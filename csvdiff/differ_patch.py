"""Patch generation: convert a DiffResult into a list of patch operations
that can be applied to reproduce the changes."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult, RowChange


class PatchError(Exception):
    pass


@dataclass
class PatchOp:
    op: str          # 'add' | 'remove' | 'replace'
    key: tuple
    old: Optional[Dict[str, str]] = None
    new: Optional[Dict[str, str]] = None


@dataclass
class Patch:
    ops: List[PatchOp] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.ops)

    def __iter__(self):
        return iter(self.ops)


def build_patch(result: DiffResult) -> Patch:
    """Build a Patch from a DiffResult."""
    if result is None:
        raise PatchError("result must not be None")
    ops: List[PatchOp] = []
    for key, row in result.added.items():
        ops.append(PatchOp(op="add", key=key, new=row))
    for key, row in result.removed.items():
        ops.append(PatchOp(op="remove", key=key, old=row))
    for key, change in result.changed.items():
        ops.append(PatchOp(op="replace", key=key, old=change.old_row, new=change.new_row))
    return Patch(ops=ops)


def apply_patch(rows: Dict[tuple, Dict[str, str]], patch: Patch) -> Dict[tuple, Dict[str, str]]:
    """Apply a Patch to a dict of rows keyed by tuple, returning updated rows."""
    if patch is None:
        raise PatchError("patch must not be None")
    result = dict(rows)
    for op in patch:
        if op.op == "add":
            result[op.key] = op.new
        elif op.op == "remove":
            result.pop(op.key, None)
        elif op.op == "replace":
            result[op.key] = op.new
        else:
            raise PatchError(f"Unknown op: {op.op!r}")
    return result


def invert_patch(patch: Patch) -> Patch:
    """Return the inverse patch (undo)."""
    if patch is None:
        raise PatchError("patch must not be None")
    inv: List[PatchOp] = []
    for op in patch:
        if op.op == "add":
            inv.append(PatchOp(op="remove", key=op.key, old=op.new))
        elif op.op == "remove":
            inv.append(PatchOp(op="add", key=op.key, new=op.old))
        elif op.op == "replace":
            inv.append(PatchOp(op="replace", key=op.key, old=op.new, new=op.old))
    return Patch(ops=inv)
