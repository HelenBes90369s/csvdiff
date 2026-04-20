"""Dispatcher: routes DiffResult entries from a queue through a pool."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from csvdiff.differ import DiffResult
from csvdiff.differ_queue import DiffQueue, QueueEntry, QueueOptions, drain, enqueue
from csvdiff.differ_pool import PoolOptions, PoolResult, run_pool


class DispatchError(Exception):
    """Raised when the dispatcher is misconfigured."""


@dataclass
class DispatchOptions:
    queue: QueueOptions = field(default_factory=QueueOptions)
    pool: PoolOptions = field(default_factory=PoolOptions)
    stop_on_first_error: bool = False


@dataclass
class DispatchSummary:
    total: int
    succeeded: int
    failed: int
    results: List[PoolResult]

    def all_ok(self) -> bool:
        return self.failed == 0


def dispatch(
    entries: List[QueueEntry],
    fn: Callable[[QueueEntry], DiffResult],
    options: Optional[DispatchOptions] = None,
) -> DispatchSummary:
    """Enqueue *entries*, run *fn* via pool, return a summary."""
    if entries is None:
        raise DispatchError("entries must not be None")
    if not callable(fn):
        raise DispatchError("fn must be callable")

    opts = options or DispatchOptions()
    queue = DiffQueue(options=opts.queue)

    for e in entries:
        enqueue(queue, e)

    queued: List[QueueEntry] = []
    drain(queue, queued.append)

    pool_results = run_pool(queued, fn, opts.pool)

    succeeded = sum(1 for r in pool_results if r.ok())
    failed = sum(1 for r in pool_results if not r.ok())

    if opts.stop_on_first_error and failed:
        first_err = next(r for r in pool_results if not r.ok())
        raise DispatchError(
            f"job '{first_err.job_id}' failed: {first_err.error}"
        )

    return DispatchSummary(
        total=len(pool_results),
        succeeded=succeeded,
        failed=failed,
        results=pool_results,
    )
