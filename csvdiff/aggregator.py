"""Aggregate numeric field changes across a DiffResult."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from csvdiff.differ import DiffResult, RowChange


class AggregateError(Exception):
    """Raised when aggregation cannot be performed."""


@dataclass
class FieldAggregate:
    """Aggregated statistics for a single field across all changed rows."""
    field_name: str
    count: int = 0
    numeric_count: int = 0
    total_delta: float = 0.0
    min_delta: Optional[float] = None
    max_delta: Optional[float] = None

    @property
    def mean_delta(self) -> Optional[float]:
        if self.numeric_count == 0:
            return None
        return self.total_delta / self.numeric_count


def _try_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def aggregate_diff(
    result: DiffResult,
    columns: Optional[List[str]] = None,
) -> Dict[str, FieldAggregate]:
    """Compute per-field numeric deltas across all changed rows.

    Args:
        result: The diff result to aggregate.
        columns: Optional list of field names to restrict aggregation to.
                 If *None*, all changed fields are included.

    Returns:
        A mapping of field name -> :class:`FieldAggregate`.

    Raises:
        AggregateError: If *columns* contains an empty or whitespace-only name.
    """
    if result is None:
        raise AggregateError("result must not be None")

    if columns is not None:
        for col in columns:
            if not col or not col.strip():
                raise AggregateError("column names must not be empty or whitespace")
        allowed = set(columns)
    else:
        allowed = None

    aggregates: Dict[str, FieldAggregate] = {}

    for change in result.changed:
        for fc in change.field_changes:
            name = fc.field
            if allowed is not None and name not in allowed:
                continue
            if name not in aggregates:
                aggregates[name] = FieldAggregate(field_name=name)
            agg = aggregates[name]
            agg.count += 1
            old = _try_float(fc.old_value)
            new = _try_float(fc.new_value)
            if old is not None and new is not None:
                delta = new - old
                agg.numeric_count += 1
                agg.total_delta += delta
                agg.min_delta = delta if agg.min_delta is None else min(agg.min_delta, delta)
                agg.max_delta = delta if agg.max_delta is None else max(agg.max_delta, delta)

    return aggregates
