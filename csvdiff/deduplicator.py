"""Deduplicator: remove duplicate RowChange entries from a DiffResult.

Two RowChange entries are considered duplicates when they share the same
row key *and* the same change kind (added / removed / changed).  For
'changed' rows the set of FieldChange objects is also compared so that
two 'changed' entries with different field mutations are kept separate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from csvdiff.differ import DiffResult, RowChange


class DeduplicateError(Exception):
    """Raised when deduplication cannot be performed."""


@dataclass(frozen=True)
class DeduplicateOptions:
    """Configuration for deduplication behaviour."""

    keep: str = "first"  # 'first' | 'last'

    def __post_init__(self) -> None:
        if self.keep not in ("first", "last"):
            raise DeduplicateError(
                f"keep must be 'first' or 'last', got {self.keep!r}"
            )


def _row_signature(change: RowChange) -> Tuple:
    """Return a hashable signature that uniquely identifies a RowChange."""
    field_sig = frozenset(
        (fc.field, fc.old_value, fc.new_value) for fc in (change.fields or [])
    )
    return (change.key, change.kind, field_sig)


def count_duplicates(result: DiffResult) -> int:
    """Return the number of duplicate RowChange entries in *result*.

    A duplicate is any RowChange whose signature has already appeared in
    an earlier position within ``result.changes``.

    Parameters
    ----------
    result:
        The diff result to inspect.

    Returns
    -------
    int
        The count of duplicate (non-unique) entries.
    """
    seen: set = set()
    duplicates = 0
    for change in result.changes:
        sig = _row_signature(change)
        if sig in seen:
            duplicates += 1
        else:
            seen.add(sig)
    return duplicates


def deduplicate_diff(
    result: DiffResult,
    options: DeduplicateOptions | None = None,
) -> DiffResult:
    """Return a new DiffResult with duplicate RowChange entries removed.

    Parameters
    ----------
    result:
        The diff result to deduplicate.
    options:
        Controls which duplicate to keep (default: first occurrence).

    Returns
    -------
    DiffResult
        A new DiffResult containing only unique RowChange entries.
    """
    if options is None:
        options = DeduplicateOptions()

    changes: List[RowChange] = list(result.changes)
    if options.keep == "last":
        changes = list(reversed(changes))

    seen: set = set()
    unique: List[RowChange] = []
    for change in changes:
        sig = _row_signature(change)
        if sig not in seen:
            seen.add(sig)
            unique.append(change)

    if options.keep == "last":
        unique = list(reversed(unique))

    return DiffResult(
        added=result.added,
        removed=result.removed,
        changes=unique,
    )
