"""Trim leading/trailing whitespace from row values in a DiffResult."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from csvdiff.differ import DiffResult, RowChange, FieldChange


class TrimError(ValueError):
    """Raised when trimmer receives invalid input."""


@dataclass(frozen=True)
class TrimOptions:
    columns: List[str] | None = None  # None means all columns
    trim_keys: bool = False

    def __post_init__(self) -> None:
        if self.columns is not None and len(self.columns) == 0:
            raise TrimError("columns must be None or a non-empty list")


def _trim_row(row: dict, opts: TrimOptions) -> dict:
    result = {}
    for k, v in row.items():
        col_match = opts.columns is None or k in opts.columns
        new_v = v.strip() if col_match and isinstance(v, str) else v
        new_k = k.strip() if opts.trim_keys and isinstance(k, str) else k
        result[new_k] = new_v
    return result


def _trim_field_changes(changes: List[FieldChange], opts: TrimOptions) -> List[FieldChange]:
    out = []
    for fc in changes:
        col_match = opts.columns is None or fc.field in opts.columns
        if col_match:
            old = fc.old_value.strip() if isinstance(fc.old_value, str) else fc.old_value
            new = fc.new_value.strip() if isinstance(fc.new_value, str) else fc.new_value
        else:
            old, new = fc.old_value, fc.new_value
        field = fc.field.strip() if opts.trim_keys and isinstance(fc.field, str) else fc.field
        out.append(FieldChange(field=field, old_value=old, new_value=new))
    return out


def trim_diff(result: DiffResult | None, opts: TrimOptions | None = None) -> DiffResult:
    """Return a new DiffResult with string values trimmed according to opts."""
    if result is None:
        raise TrimError("result must not be None")
    if opts is None:
        opts = TrimOptions()

    added = [_trim_row(r, opts) for r in result.added]
    removed = [_trim_row(r, opts) for r in result.removed]
    changed = [
        RowChange(
            key=rc.key,
            old_row=_trim_row(rc.old_row, opts),
            new_row=_trim_row(rc.new_row, opts),
            field_changes=_trim_field_changes(rc.field_changes, opts),
        )
        for rc in result.changed
    ]
    return DiffResult(added=added, removed=removed, changed=changed)
