"""Merge a DiffResult back into a base CSV, producing an updated dataset."""

from __future__ import annotations

from typing import Dict, List, Tuple

from csvdiff.differ import DiffResult


class MergeError(Exception):
    """Raised when a merge cannot be completed cleanly."""


def merge_diff(
    base_rows: List[Dict[str, str]],
    key_columns: List[str],
    diff: DiffResult,
) -> List[Dict[str, str]]:
    """Apply *diff* to *base_rows* and return the merged row list.

    Rules
    -----
    - Added rows in *diff* are appended.
    - Removed rows are dropped (a row missing from base raises :class:`MergeError`).
    - Changed rows have their fields updated in-place.

    Raises
    ------
    MergeError
        If *key_columns* is empty, a key column is missing from a row, duplicate
        keys exist in *base_rows*, or the diff references keys inconsistent with
        the base (e.g. removing a non-existent row or adding a duplicate).
    """
    if not key_columns:
        raise MergeError("At least one key column is required for merging.")

    def row_key(row: Dict[str, str]) -> Tuple[str, ...]:
        try:
            return tuple(row[k] for k in key_columns)
        except KeyError as exc:
            raise MergeError(f"Key column {exc} missing from row: {row}") from exc

    # Index base rows by key for O(1) lookup; preserve insertion order via list.
    index: Dict[Tuple[str, ...], Dict[str, str]] = {}
    order: List[Tuple[str, ...]] = []
    for row in base_rows:
        k = row_key(row)
        if k in index:
            raise MergeError(f"Duplicate key in base rows: {k}")
        index[k] = dict(row)
        order.append(k)

    # Apply removals.
    for key, removed_row in diff.removed.items():
        if key not in index:
            raise MergeError(f"Cannot remove row with key {key!r}: not found in base.")
        del index[key]
        order.remove(key)

    # Apply changes.
    for key, change in diff.changed.items():
        if key not in index:
            raise MergeError(f"Cannot update row with key {key!r}: not found in base.")
        for field_change in change.field_changes:
            if field_change.column not in index[key]:
                raise MergeError(
                    f"Cannot update field {field_change.column!r} for key {key!r}: "
                    "column not present in base row."
                )
            index[key][field_change.column] = field_change.new_value

    # Apply additions.
    for key, added_row in diff.added.items():
        if key in index:
            raise MergeError(f"Cannot add row with key {key!r}: already exists in base.")
        index[key] = dict(added_row)
        order.append(key)

    return [index[k] for k in order]
