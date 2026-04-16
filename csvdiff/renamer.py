"""Rename columns across a DiffResult."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from csvdiff.differ import DiffResult, RowChange, FieldChange


class RenameError(Exception):
    pass


@dataclass(frozen=True)
class RenameOptions:
    mapping: Dict[str, str]

    def __post_init__(self) -> None:
        if not self.mapping:
            raise RenameError("mapping must not be empty")
        for k, v in self.mapping.items():
            if not k or not k.strip():
                raise RenameError("mapping keys must be non-empty strings")
            if not v or not v.strip():
                raise RenameError("mapping values must be non-empty strings")


def _rename_row(row: Dict[str, str], mapping: Dict[str, str]) -> Dict[str, str]:
    return {mapping.get(k, k): v for k, v in row.items()}


def _rename_field_change(fc: FieldChange, mapping: Dict[str, str]) -> FieldChange:
    return FieldChange(
        field=mapping.get(fc.field, fc.field),
        old_value=fc.old_value,
        new_value=fc.new_value,
    )


def _rename_row_change(rc: RowChange, mapping: Dict[str, str]) -> RowChange:
    return RowChange(
        key=rc.key,
        kind=rc.kind,
        old_row=_rename_row(rc.old_row, mapping) if rc.old_row else rc.old_row,
        new_row=_rename_row(rc.new_row, mapping) if rc.new_row else rc.new_row,
        field_changes=[_rename_field_change(fc, mapping) for fc in rc.field_changes],
    )


def rename_diff(result: DiffResult, options: RenameOptions) -> DiffResult:
    if result is None:
        raise RenameError("result must not be None")
    mapping = options.mapping
    return DiffResult(
        added=[_rename_row(r, mapping) for r in result.added],
        removed=[_rename_row(r, mapping) for r in result.removed],
        changed=[_rename_row_change(rc, mapping) for rc in result.changed],
    )
