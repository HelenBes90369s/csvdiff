"""Buffered accumulation of DiffResult objects up to a capacity limit."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from csvdiff.differ import DiffResult, RowChange


class BufferError(Exception):
    """Raised when buffer operations are invalid."""


@dataclass
class BufferOptions:
    max_size: int = 1000
    overflow: str = "drop"  # "drop" | "raise" | "flush"

    def __post_init__(self) -> None:
        if self.max_size <= 0:
            raise BufferError("max_size must be a positive integer")
        if self.overflow not in ("drop", "raise", "flush"):
            raise BufferError("overflow must be 'drop', 'raise', or 'flush'")


@dataclass
class BufferState:
    options: BufferOptions
    _changes: List[RowChange] = field(default_factory=list)
    _flushed: int = 0

    @property
    def size(self) -> int:
        return len(self._changes)

    @property
    def is_full(self) -> bool:
        return self.size >= self.options.max_size

    @property
    def total_flushed(self) -> int:
        return self._flushed


def push(state: BufferState, change: RowChange) -> bool:
    """Add a change to the buffer.  Returns True if accepted, False if dropped."""
    if state is None:
        raise BufferError("state must not be None")
    if change is None:
        raise BufferError("change must not be None")
    if state.is_full:
        if state.options.overflow == "raise":
            raise BufferError("buffer is full")
        if state.options.overflow == "drop":
            return False
        # flush
        flush(state)
    state._changes.append(change)
    return True


def flush(state: BufferState) -> DiffResult:
    """Drain the buffer and return a DiffResult containing accumulated changes."""
    if state is None:
        raise BufferError("state must not be None")
    result = DiffResult(
        added=list(state._changes),
        removed=[],
        changed=[],
    )
    state._flushed += state.size
    state._changes.clear()
    return result


def drain(state: BufferState) -> DiffResult:
    """Alias for flush — empties the buffer and returns contents."""
    return flush(state)
