"""Limit the number of changes returned in a DiffResult."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from csvdiff.differ import DiffResult, RowChange


class LimitError(ValueError):
    """Raised when limiter options are invalid."""


@dataclass(frozen=True)
class LimitOptions:
    max_added: Optional[int] = None
    max_removed: Optional[int] = None
    max_changed: Optional[int] = None

    def __post_init__(self) -> None:
        for name, value in [
            ("max_added", self.max_added),
            ("max_removed", self.max_removed),
            ("max_changed", self.max_changed),
        ]:
            if value is not None and value < 0:
                raise LimitError(f"{name} must be non-negative, got {value}")


@dataclass(frozen=True)
class LimitResult:
    result: DiffResult
    added_truncated: bool
    removed_truncated: bool
    changed_truncated: bool

    @property
    def any_truncated(self) -> bool:
        return self.added_truncated or self.removed_truncated or self.changed_truncated


def _apply_limit(
    rows: list[RowChange], limit: Optional[int]
) -> tuple[list[RowChange], bool]:
    if limit is None or len(rows) <= limit:
        return rows, False
    return rows[:limit], True


def limit_diff(result: DiffResult, options: LimitOptions) -> LimitResult:
    """Return a new DiffResult with each change category capped to the given limits."""
    added, added_truncated = _apply_limit(result.added, options.max_added)
    removed, removed_truncated = _apply_limit(result.removed, options.max_removed)
    changed, changed_truncated = _apply_limit(result.changed, options.max_changed)

    limited = DiffResult(added=added, removed=removed, changed=changed)
    return LimitResult(
        result=limited,
        added_truncated=added_truncated,
        removed_truncated=removed_truncated,
        changed_truncated=changed_truncated,
    )
