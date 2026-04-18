"""Sliding-window view over a DiffResult's changes."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from csvdiff.differ import DiffResult, RowChange


class WindowError(ValueError):
    pass


@dataclass
class WindowOptions:
    size: int = 10
    step: int = 1

    def __post_init__(self) -> None:
        if self.size <= 0:
            raise WindowError("size must be positive")
        if self.step <= 0:
            raise WindowError("step must be positive")


@dataclass
class DiffWindow:
    index: int
    changes: List[RowChange]

    @property
    def is_empty(self) -> bool:
        return len(self.changes) == 0


def window_diff(
    result: Optional[DiffResult],
    options: Optional[WindowOptions] = None,
) -> List[DiffWindow]:
    """Partition changes into overlapping windows of fixed size."""
    if result is None:
        raise WindowError("result must not be None")
    opts = options or WindowOptions()
    all_changes: List[RowChange] = (
        list(result.added) + list(result.removed) + list(result.changed)
    )
    if not all_changes:
        return [DiffWindow(index=0, changes=[])]
    windows: List[DiffWindow] = []
    i = 0
    idx = 0
    while i < len(all_changes):
        chunk = all_changes[i : i + opts.size]
        windows.append(DiffWindow(index=idx, changes=chunk))
        i += opts.step
        idx += 1
    return windows


def total_windows(result: Optional[DiffResult], options: Optional[WindowOptions] = None) -> int:
    return len(window_diff(result, options))
