"""Conflict resolution for overlapping diff results."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal, Sequence
from csvdiff.differ import DiffResult, RowChange


class ResolveError(Exception):
    pass


Strategy = Literal["left", "right", "union", "intersection"]


@dataclass(frozen=True)
class ResolveOptions:
    strategy: Strategy = "left"

    def __post_init__(self) -> None:
        valid = {"left", "right", "union", "intersection"}
        if self.strategy not in valid:
            raise ResolveError(f"strategy must be one of {valid}, got {self.strategy!r}")


def _key(change: RowChange) -> tuple:
    return change.key


def resolve_diff(
    left: DiffResult,
    right: DiffResult,
    options: ResolveOptions | None = None,
) -> DiffResult:
    """Merge two DiffResults according to the chosen strategy."""
    if left is None or right is None:
        raise ResolveError("left and right must not be None")
    opts = options or ResolveOptions()

    def _index(changes: Sequence[RowChange]) -> dict:
        return {_key(c): c for c in changes}

    def _resolve_changes(
        l_changes: Sequence[RowChange], r_changes: Sequence[RowChange]
    ) -> list[RowChange]:
        li, ri = _index(l_changes), _index(r_changes)
        if opts.strategy == "left":
            return list(l_changes)
        if opts.strategy == "right":
            return list(r_changes)
        if opts.strategy == "union":
            merged = {**ri, **li}  # left wins on conflict
            return list(merged.values())
        # intersection
        common_keys = li.keys() & ri.keys()
        return [li[k] for k in common_keys]

    return DiffResult(
        added=_resolve_changes(left.added, right.added),
        removed=_resolve_changes(left.removed, right.removed),
        changed=_resolve_changes(left.changed, right.changed),
    )
