"""Redact sensitive field values in a DiffResult."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from csvdiff.differ import DiffResult, FieldChange, RowChange


_REDACTED = "***"


class RedactError(Exception):
    """Raised when redaction cannot be applied."""


@dataclass
class RedactOptions:
    """Configuration for field redaction."""

    columns: Set[str] = field(default_factory=set)
    placeholder: str = _REDACTED

    def __post_init__(self) -> None:
        if not self.columns:
            raise RedactError("columns must not be empty")
        if not self.placeholder:
            raise RedactError("placeholder must not be empty")


def _redact_value(value: Optional[str], placeholder: str) -> Optional[str]:
    """Return placeholder if value is not None, otherwise None."""
    return placeholder if value is not None else None


def _redact_row(row: Optional[Dict[str, str]], opts: RedactOptions) -> Optional[Dict[str, str]]:
    if row is None:
        return None
    return {
        k: (opts.placeholder if k in opts.columns else v)
        for k, v in row.items()
    }


def _redact_field_changes(
    field_changes: List[FieldChange], opts: RedactOptions
) -> List[FieldChange]:
    result = []
    for fc in field_changes:
        if fc.field in opts.columns:
            result.append(
                FieldChange(
                    field=fc.field,
                    old_value=_redact_value(fc.old_value, opts.placeholder),
                    new_value=_redact_value(fc.new_value, opts.placeholder),
                )
            )
        else:
            result.append(fc)
    return result


def _redact_change(change: RowChange, opts: RedactOptions) -> RowChange:
    return RowChange(
        key=change.key,
        old_row=_redact_row(change.old_row, opts),
        new_row=_redact_row(change.new_row, opts),
        field_changes=_redact_field_changes(change.field_changes, opts),
    )


def redact_diff(
    result: Optional[DiffResult],
    opts: Optional[RedactOptions] = None,
) -> DiffResult:
    """Return a new DiffResult with sensitive columns redacted."""
    if result is None:
        raise RedactError("result must not be None")
    if opts is None:
        raise RedactError("opts must not be None")

    return DiffResult(
        added=[_redact_row(r, opts) for r in result.added],  # type: ignore[misc]
        removed=[_redact_row(r, opts) for r in result.removed],  # type: ignore[misc]
        changed=[_redact_change(c, opts) for c in result.changed],
    )
