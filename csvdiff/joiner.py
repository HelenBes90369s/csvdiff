"""Join two DiffResults into one, merging their changes by key."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from csvdiff.differ import DiffResult, RowChange


class JoinError(Exception):
    """Raised when joining two DiffResults fails."""


@dataclass(frozen=True)
class JoinOptions:
    strategy: str = "union"  # "union" | "intersection" | "left" | "right"

    def __post_init__(self) -> None:
        valid = {"union", "intersection", "left", "right"}
        if self.strategy not in valid:
            raise JoinError(
                f"Invalid strategy {self.strategy!r}; expected one of {sorted(valid)}"
            )


def _index(result: DiffResult) -> dict:
    """Return a mapping of row_key -> RowChange."""
    return {tuple(c.key) if isinstance(c.key, list) else c.key: c for c in result.changes}


def join_diff(
    left: DiffResult,
    right: DiffResult,
    options: Optional[JoinOptions] = None,
) -> DiffResult:
    """Combine *left* and *right* DiffResults according to *options.strategy*.

    - ``union``        – all changes from either side (left wins on conflict)
    - ``intersection`` – only changes whose key appears in both
    - ``left``         – only changes from *left*
    - ``right``        – only changes from *right*
    """
    if left is None or right is None:
        raise JoinError("Both left and right DiffResult must be provided")

    opts = options or JoinOptions()
    li = _index(left)
    ri = _index(right)

    if opts.strategy == "left":
        changes: List[RowChange] = list(left.changes)
    elif opts.strategy == "right":
        changes = list(right.changes)
    elif opts.strategy == "intersection":
        changes = [li[k] for k in li if k in ri]
    else:  # union
        merged = {**ri, **li}  # left wins
        changes = list(merged.values())

    return DiffResult(
        added=sorted({tuple(c.key) if isinstance(c.key, list) else c.key for c in changes if c.kind == "added"}),
        removed=sorted({tuple(c.key) if isinstance(c.key, list) else c.key for c in changes if c.kind == "removed"}),
        changes=changes,
    )
