"""Collect timing and count metrics from a diff run."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Any

from csvdiff.differ import DiffResult


class MetricsError(Exception):
    pass


@dataclass
class MetricsOptions:
    enabled: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise MetricsError("enabled must be a bool")


@dataclass
class DiffMetrics:
    added: int
    removed: int
    changed: int
    total_changes: int
    elapsed_seconds: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "added": self.added,
            "removed": self.removed,
            "changed": self.changed,
            "total_changes": self.total_changes,
            "elapsed_seconds": self.elapsed_seconds,
        }


def collect_metrics(
    fn: Callable[[], DiffResult],
    options: MetricsOptions | None = None,
) -> tuple[DiffResult, DiffMetrics | None]:
    """Run *fn* and return its result alongside optional metrics."""
    if options is None:
        options = MetricsOptions()
    if not options.enabled:
        return fn(), None

    start = time.monotonic()
    result = fn()
    elapsed = time.monotonic() - start

    metrics = DiffMetrics(
        added=len(result.added),
        removed=len(result.removed),
        changed=len(result.changed),
        total_changes=len(result.added) + len(result.removed) + len(result.changed),
        elapsed_seconds=round(elapsed, 6),
    )
    return result, metrics
