"""Align two DiffResult objects so their changes share a common key order."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from csvdiff.differ import DiffResult, RowChange


class AlignError(Exception):
    """Raised when alignment fails."""


@dataclass
class AlignedPair:
    key: tuple
    left: RowChange | None
    right: RowChange | None


def _row_key(change: RowChange) -> tuple:
    k = change.key
    return tuple(k) if isinstance(k, (list, tuple)) else (k,)


def align_diff(
    left: DiffResult,
    right: DiffResult,
    *,
    fill_missing: bool = True,
) -> List[AlignedPair]:
    """Return a list of AlignedPair entries merging *left* and *right* by key.

    If *fill_missing* is True (default) keys present in only one side are
    included with ``None`` on the absent side.  When False only shared keys
    are returned.
    """
    if left is None or right is None:
        raise AlignError("Both left and right DiffResult must be provided.")

    left_index: dict[tuple, RowChange] = {_row_key(c): c for c in left.changes}
    right_index: dict[tuple, RowChange] = {_row_key(c): c for c in right.changes}

    if fill_missing:
        all_keys = sorted(left_index.keys() | right_index.keys())
    else:
        all_keys = sorted(left_index.keys() & right_index.keys())

    return [
        AlignedPair(
            key=k,
            left=left_index.get(k),
            right=right_index.get(k),
        )
        for k in all_keys
    ]


def aligned_keys(pairs: List[AlignedPair]) -> List[tuple]:
    """Return just the keys from a list of AlignedPair objects."""
    return [p.key for p in pairs]


def split_aligned(
    pairs: List[AlignedPair],
) -> Tuple[List[AlignedPair], List[AlignedPair], List[AlignedPair]]:
    """Split pairs into (both, left_only, right_only) groups."""
    both = [p for p in pairs if p.left is not None and p.right is not None]
    left_only = [p for p in pairs if p.left is not None and p.right is None]
    right_only = [p for p in pairs if p.left is None and p.right is not None]
    return both, left_only, right_only
