"""Async-style diff job queue for batched or deferred processing."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Deque, List, Optional

from csvdiff.differ import DiffResult


class QueueError(Exception):
    """Raised when the diff queue is misused."""


@dataclass
class QueueOptions:
    max_size: int = 0          # 0 = unlimited
    on_overflow: str = "drop"  # "drop" | "raise"

    def __post_init__(self) -> None:
        if self.max_size < 0:
            raise QueueError("max_size must be >= 0")
        if self.on_overflow not in ("drop", "raise"):
            raise QueueError("on_overflow must be 'drop' or 'raise'")


@dataclass
class QueueEntry:
    job_id: str
    result: DiffResult
    meta: dict = field(default_factory=dict)

    def ok(self) -> bool:
        r = self.result
        return not (r.added or r.removed or r.changed)


@dataclass
class DiffQueue:
    options: QueueOptions
    _items: Deque[QueueEntry] = field(default_factory=deque, init=False)

    def size(self) -> int:
        return len(self._items)

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def is_full(self) -> bool:
        return self.options.max_size > 0 and len(self._items) >= self.options.max_size


def enqueue(queue: DiffQueue, entry: QueueEntry) -> bool:
    """Add an entry to the queue. Returns True if enqueued, False if dropped."""
    if queue is None:
        raise QueueError("queue must not be None")
    if entry is None:
        raise QueueError("entry must not be None")
    if queue.is_full():
        if queue.options.on_overflow == "raise":
            raise QueueError(
                f"queue is full (max_size={queue.options.max_size})"
            )
        return False
    queue._items.append(entry)
    return True


def dequeue(queue: DiffQueue) -> Optional[QueueEntry]:
    """Remove and return the next entry, or None if empty."""
    if queue is None:
        raise QueueError("queue must not be None")
    if queue.is_empty():
        return None
    return queue._items.popleft()


def drain(queue: DiffQueue, fn: Callable[[QueueEntry], None]) -> List[QueueEntry]:
    """Process all entries with *fn* and return them in order."""
    if queue is None:
        raise QueueError("queue must not be None")
    if not callable(fn):
        raise QueueError("fn must be callable")
    processed: List[QueueEntry] = []
    while not queue.is_empty():
        entry = queue._items.popleft()
        fn(entry)
        processed.append(entry)
    return processed
