"""Rank diff changes by a configurable score or field priority."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Sequence

from csvdiff.differ import DiffResult, RowChange


class RankError(ValueError):
    """Raised when ranking configuration is invalid."""


@dataclass(frozen=True)
class RankOptions:
    field: Optional[str] = None          # rank by number of changes to this field
    by: str = "changes"                  # "changes" | "key"
    descending: bool = True

    def __post_init__(self) -> None:
        if self.by not in ("changes", "key"):
            raise RankError(f"Invalid 'by' value: {self.by!r}; must be 'changes' or 'key'")


def _change_count(change: RowChange, field: Optional[str]) -> int:
    """Return the number of field changes, optionally filtered to one field."""
    if field is None:
        return len(change.changes)
    return sum(1 for fc in change.changes if fc.field == field)


def _rank_key(opts: RankOptions) -> Callable[[RowChange], tuple]:
    if opts.by == "key":
        return lambda c: (str(c.key),)
    # default: rank by number of field changes
    return lambda c: (_change_count(c, opts.field),)


def rank_diff(
    result: DiffResult,
    opts: Optional[RankOptions] = None,
) -> List[RowChange]:
    """Return changed rows sorted by the configured ranking criterion.

    Added and removed rows are included; they count as fully changed.
    """
    if opts is None:
        opts = RankOptions()

    all_changes: List[RowChange] = [
        *result.added,
        *result.removed,
        *result.changed,
    ]

    key_fn = _rank_key(opts)
    return sorted(all_changes, key=key_fn, reverse=opts.descending)


def top_n(
    result: DiffResult,
    n: int,
    opts: Optional[RankOptions] = None,
) -> List[RowChange]:
    """Return the top *n* changes according to *opts*."""
    if n < 0:
        raise RankError(f"n must be non-negative, got {n}")
    ranked = rank_diff(result, opts)
    return ranked[:n]
