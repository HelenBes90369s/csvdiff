"""Batch diffing: run a diff function over multiple file pairs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

from csvdiff.differ import DiffResult


class BatchError(Exception):
    pass


@dataclass
class BatchOptions:
    stop_on_error: bool = False
    label_pairs: bool = True

    def __post_init__(self) -> None:
        pass  # no constraints yet


@dataclass
class BatchEntry:
    label: str
    result: Optional[DiffResult]
    error: Optional[str]

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass
class BatchResult:
    entries: List[BatchEntry] = field(default_factory=list)

    @property
    def all_ok(self) -> bool:
        return all(e.ok for e in self.entries)

    @property
    def failed(self) -> List[BatchEntry]:
        return [e for e in self.entries if not e.ok]

    @property
    def succeeded(self) -> List[BatchEntry]:
        return [e for e in self.entries if e.ok]


def run_batch(
    pairs: List[Tuple[str, str]],
    diff_fn: Callable[[str, str], DiffResult],
    options: Optional[BatchOptions] = None,
) -> BatchResult:
    """Run *diff_fn* over each (path_a, path_b) pair.

    Args:
        pairs: list of (path_a, path_b) tuples.
        diff_fn: callable that accepts two path strings and returns a DiffResult.
        options: BatchOptions controlling error handling.

    Returns:
        BatchResult aggregating all outcomes.
    """
    if pairs is None:
        raise BatchError("pairs must not be None")
    if diff_fn is None:
        raise BatchError("diff_fn must not be None")

    opts = options or BatchOptions()
    batch = BatchResult()

    for idx, (path_a, path_b) in enumerate(pairs):
        label = f"{path_a} vs {path_b}" if opts.label_pairs else str(idx)
        try:
            result = diff_fn(path_a, path_b)
            batch.entries.append(BatchEntry(label=label, result=result, error=None))
        except Exception as exc:  # noqa: BLE001
            entry = BatchEntry(label=label, result=None, error=str(exc))
            batch.entries.append(entry)
            if opts.stop_on_error:
                raise BatchError(f"Batch stopped on error at pair {idx}: {exc}") from exc

    return batch
