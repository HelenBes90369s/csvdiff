"""Row-level change scoring: assign a numeric severity score to each RowChange."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from csvdiff.differ import DiffResult, RowChange


class WeightError(Exception):
    pass


@dataclass
class WeightOptions:
    weights: Dict[str, float] = field(default_factory=dict)
    default_weight: float = 1.0
    missing_penalty: float = 0.0

    def __post_init__(self) -> None:
        if self.default_weight < 0:
            raise WeightError("default_weight must be >= 0")
        if self.missing_penalty < 0:
            raise WeightError("missing_penalty must be >= 0")
        for col, w in self.weights.items():
            if w < 0:
                raise WeightError(f"weight for '{col}' must be >= 0")


@dataclass
class ScoredChange:
    change: RowChange
    score: float


def _score_change(change: RowChange, opts: WeightOptions) -> float:
    if change.added_row is not None and change.removed_row is None:
        return opts.missing_penalty
    if change.removed_row is not None and change.added_row is None:
        return opts.missing_penalty
    total = 0.0
    for fc in change.field_changes:
        total += opts.weights.get(fc.field, opts.default_weight)
    return total


def score_changes(
    result: DiffResult,
    opts: Optional[WeightOptions] = None,
) -> List[ScoredChange]:
    if result is None:
        raise WeightError("result must not be None")
    if opts is None:
        opts = WeightOptions()
    return [ScoredChange(change=c, score=_score_change(c, opts)) for c in result.changes]


def top_changes(
    scored: List[ScoredChange],
    n: int = 10,
) -> List[ScoredChange]:
    if n < 0:
        raise WeightError("n must be >= 0")
    return sorted(scored, key=lambda s: s.score, reverse=True)[:n]
