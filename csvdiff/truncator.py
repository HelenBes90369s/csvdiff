"""Truncate a DiffResult to a maximum number of changes per change type."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from csvdiff.differ import DiffResult, RowChange


class TruncateError(ValueError):
    """Raised when truncation parameters are invalid."""


@dataclass
class TruncateOptions:
    max_added: Optional[int] = None
    max_removed: Optional[int] = None
    max_changed: Optional[int] = None

    def __post_init__(self) -> None:
        for name, val in [
            ("max_added", self.max_added),
            ("max_removed", self.max_removed),
            ("max_changed", self.max_changed),
        ]:
            if val is not None and val < 0:
                raise TruncateError(f"{name} must be >= 0, got {val}")


@dataclass
class TruncateResult:
    diff: DiffResult
    added_truncated: bool
    removed_truncated: bool
    changed_truncated: bool

    @property
    def any_truncated(self) -> bool:
        return self.added_truncated or self.removed_truncated or self.changed_truncated


def _cap(rows: list[RowChange], limit: Optional[int]) -> tuple[list[RowChange], bool]:
    if limit is None or len(rows) <= limit:
        return rows, False
    return rows[:limit], True


def truncate_diff(result: DiffResult, opts: TruncateOptions) -> TruncateResult:
    """Return a new DiffResult with each change list capped to the given limits."""
    added, added_trunc = _cap(result.added, opts.max_added)
    removed, removed_trunc = _cap(result.removed, opts.max_removed)
    changed, changed_trunc = _cap(result.changed, opts.max_changed)

    truncated = DiffResult(
        added=added,
        removed=removed,
        changed=changed,
    )
    return TruncateResult(
        diff=truncated,
        added_truncated=added_trunc,
        removed_truncated=removed_trunc,
        changed_truncated=changed_trunc,
    )
