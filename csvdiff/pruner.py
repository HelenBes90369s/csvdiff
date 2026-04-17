"""pruner.py – remove rows from a DiffResult that match a predicate."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from csvdiff.differ import DiffResult, RowChange


class PruneError(ValueError):
    """Raised when pruning arguments are invalid."""


@dataclass(frozen=True)
class PruneOptions:
    predicate: Callable[[RowChange], bool]
    invert: bool = False

    def __post_init__(self) -> None:
        if not callable(self.predicate):
            raise PruneError("predicate must be callable")


@dataclass(frozen=True)
class PruneResult:
    result: DiffResult
    pruned_count: int


def prune_diff(result: DiffResult | None, options: PruneOptions) -> PruneResult:
    """Return a new DiffResult with matching RowChanges removed.

    When *options.invert* is True the predicate is negated – only rows that
    match are *kept* (i.e. a filter rather than a prune).
    """
    if result is None:
        raise PruneError("result must not be None")
    if options is None:
        raise PruneError("options must not be None")

    kept: list[RowChange] = []
    pruned = 0
    for change in result.changes:
        match = options.predicate(change)
        if options.invert:
            match = not match
        if match:
            pruned += 1
        else:
            kept.append(change)

    new_result = DiffResult(
        added=result.added,
        removed=result.removed,
        changes=kept,
    )
    return PruneResult(result=new_result, pruned_count=pruned)
