"""Normalizer: strip and case-fold values in CSV rows before diffing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from csvdiff.differ import DiffResult, RowChange, FieldChange


class NormalizeError(ValueError):
    """Raised when normalization configuration is invalid."""


@dataclass
class NormalizeOptions:
    strip_whitespace: bool = True
    lowercase: bool = False
    columns: Optional[List[str]] = None  # None means all columns

    def __post_init__(self) -> None:
        if self.columns is not None and len(self.columns) == 0:
            raise NormalizeError("columns list must not be empty when provided")


def normalize_value(value: str, opts: NormalizeOptions) -> str:
    """Apply normalization rules to a single string value."""
    if opts.strip_whitespace:
        value = value.strip()
    if opts.lowercase:
        value = value.lower()
    return value


def normalize_row(row: Dict[str, str], opts: NormalizeOptions) -> Dict[str, str]:
    """Return a new row dict with values normalized according to *opts*."""
    target = set(opts.columns) if opts.columns is not None else None
    return {
        k: (normalize_value(v, opts) if target is None or k in target else v)
        for k, v in row.items()
    }


def normalize_rows(
    rows: Iterable[Dict[str, str]], opts: NormalizeOptions
) -> List[Dict[str, str]]:
    """Normalize an iterable of row dicts."""
    return [normalize_row(r, opts) for r in rows]


def normalize_diff(result: DiffResult, opts: NormalizeOptions) -> DiffResult:
    """Return a new DiffResult with all row/field values normalized."""

    def _norm_fields(fields: List[FieldChange]) -> List[FieldChange]:
        return [
            FieldChange(
                field=fc.field,
                old_value=normalize_value(fc.old_value, opts),
                new_value=normalize_value(fc.new_value, opts),
            )
            for fc in fields
        ]

    def _norm_change(rc: RowChange) -> RowChange:
        return RowChange(
            key=rc.key,
            kind=rc.kind,
            old_row=normalize_row(rc.old_row, opts) if rc.old_row else rc.old_row,
            new_row=normalize_row(rc.new_row, opts) if rc.new_row else rc.new_row,
            field_changes=_norm_fields(rc.field_changes),
        )

    return DiffResult(
        added=[_norm_change(r) for r in result.added],
        removed=[_norm_change(r) for r in result.removed],
        changed=[_norm_change(r) for r in result.changed],
    )
