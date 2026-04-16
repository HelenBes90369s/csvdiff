"""masker.py — mask (partially redact) field values in a DiffResult."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from csvdiff.differ import DiffResult, RowChange, FieldChange


class MaskError(Exception):
    pass


@dataclass(frozen=True)
class MaskOptions:
    columns: tuple[str, ...]
    visible_prefix: int = 2
    visible_suffix: int = 0
    char: str = "*"

    def __post_init__(self) -> None:
        if not self.columns:
            raise MaskError("columns must not be empty")
        if self.visible_prefix < 0 or self.visible_suffix < 0:
            raise MaskError("visible_prefix and visible_suffix must be >= 0")
        if not self.char:
            raise MaskError("char must not be empty")


def _mask_value(value: str, opts: MaskOptions) -> str:
    n = len(value)
    pre = min(opts.visible_prefix, n)
    suf = min(opts.visible_suffix, n - pre)
    hidden = n - pre - suf
    if hidden <= 0:
        return value
    return value[:pre] + opts.char * hidden + (value[n - suf:] if suf else "")


def _mask_row(row: dict[str, str], opts: MaskOptions) -> dict[str, str]:
    return {k: (_mask_value(v, opts) if k in opts.columns else v) for k, v in row.items()}


def _mask_field_changes(changes: list[FieldChange], opts: MaskOptions) -> list[FieldChange]:
    out = []
    for fc in changes:
        if fc.field in opts.columns:
            out.append(FieldChange(fc.field, _mask_value(fc.old_value, opts), _mask_value(fc.new_value, opts)))
        else:
            out.append(fc)
    return out


def mask_diff(result: Optional[DiffResult], opts: MaskOptions) -> DiffResult:
    if result is None:
        raise MaskError("result must not be None")
    masked_added = [_mask_row(r, opts) for r in result.added]
    masked_removed = [_mask_row(r, opts) for r in result.removed]
    masked_changed = [
        RowChange(
            key=rc.key,
            old_row=_mask_row(rc.old_row, opts),
            new_row=_mask_row(rc.new_row, opts),
            field_changes=_mask_field_changes(rc.field_changes, opts),
        )
        for rc in result.changed
    ]
    return DiffResult(added=masked_added, removed=masked_removed, changed=masked_changed)
