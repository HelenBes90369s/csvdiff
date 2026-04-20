"""Worker pool abstraction for parallel diff processing."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Callable, Dict, List

from csvdiff.differ import DiffResult
from csvdiff.differ_queue import QueueEntry


class PoolError(Exception):
    """Raised when the pool is misconfigured or a job fails fatally."""


@dataclass
class PoolOptions:
    workers: int = 2
    timeout: float = 30.0
    reraise: bool = False

    def __post_init__(self) -> None:
        if self.workers < 1:
            raise PoolError("workers must be >= 1")
        if self.timeout <= 0:
            raise PoolError("timeout must be > 0")


@dataclass
class PoolResult:
    job_id: str
    result: DiffResult
    error: str = ""

    def ok(self) -> bool:
        return self.error == ""


def run_pool(
    entries: List[QueueEntry],
    fn: Callable[[QueueEntry], DiffResult],
    options: PoolOptions | None = None,
) -> List[PoolResult]:
    """Run *fn* over *entries* in a thread pool and return ordered results."""
    if entries is None:
        raise PoolError("entries must not be None")
    if not callable(fn):
        raise PoolError("fn must be callable")
    opts = options or PoolOptions()
    results: Dict[str, PoolResult] = {}

    with ThreadPoolExecutor(max_workers=opts.workers) as ex:
        futures = {ex.submit(fn, e): e for e in entries}
        for fut in as_completed(futures, timeout=opts.timeout):
            entry = futures[fut]
            try:
                diff = fut.result()
                results[entry.job_id] = PoolResult(
                    job_id=entry.job_id, result=diff
                )
            except Exception as exc:  # noqa: BLE001
                if opts.reraise:
                    raise PoolError(
                        f"job '{entry.job_id}' failed: {exc}"
                    ) from exc
                results[entry.job_id] = PoolResult(
                    job_id=entry.job_id,
                    result=DiffResult(added=[], removed=[], changed=[]),
                    error=str(exc),
                )

    # Return in original submission order
    return [results[e.job_id] for e in entries if e.job_id in results]
