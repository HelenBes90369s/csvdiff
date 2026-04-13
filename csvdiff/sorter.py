"""Sorting utilities for DiffResult output."""

from typing import List, Optional
from csvdiff.differ import DiffResult, RowChange


SORTABLE_FIELDS = ("key", "change_type")


class SortError(Exception):
    """Raised when an invalid sort field is specified."""


def _normalise_key(k):
    """Normalise a key to a tuple for stable, consistent comparisons."""
    return k if isinstance(k, tuple) else (k,)


def sort_diff(
    result: DiffResult,
    by: str = "key",
    reverse: bool = False,
) -> DiffResult:
    """Return a new DiffResult with rows sorted by the given field.

    Parameters
    ----------
    result:
        The diff result to sort.
    by:
        Field to sort by. One of ``'key'`` or ``'change_type'``.
    reverse:
        If ``True``, sort in descending order.

    Returns
    -------
    DiffResult
        A new DiffResult with sorted ``changes`` list and the same
        ``added`` / ``removed`` mappings.
    """
    if by not in SORTABLE_FIELDS:
        raise SortError(
            f"Invalid sort field {by!r}. Choose from: {', '.join(SORTABLE_FIELDS)}"
        )

    def _key(change: RowChange):
        if by == "key":
            # Keys may be tuples or scalars; normalise to tuple for stable sort.
            return _normalise_key(change.key)
        # change_type is a string like 'added', 'removed', 'changed'
        return (change.change_type,)

    sorted_changes: List[RowChange] = sorted(result.changes, key=_key, reverse=reverse)

    return DiffResult(
        changes=sorted_changes,
        added=result.added,
        removed=result.removed,
    )


def sort_keys(keys: List, reverse: bool = False) -> List:
    """Sort a flat list of keys, handling both scalar and tuple keys."""
    return sorted(keys, key=_normalise_key, reverse=reverse)
