"""Progress tracking for long-running diff operations."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Iterable, Iterator, TypeVar

T = TypeVar("T")


class ProgressError(Exception):
    pass


@dataclass
class ProgressOptions:
    total: int = 0
    callback: Callable[[int, int, float], None] | None = None
    interval: float = 0.1

    def __post_init__(self) -> None:
        if self.total < 0:
            raise ProgressError("total must be >= 0")
        if self.interval <= 0:
            raise ProgressError("interval must be > 0")


@dataclass
class ProgressState:
    options: ProgressOptions
    processed: int = 0
    _last_report: float = field(default_factory=time.monotonic, repr=False)

    def advance(self, n: int = 1) -> None:
        self.processed += n
        now = time.monotonic()
        if now - self._last_report >= self.options.interval:
            self._report()
            self._last_report = now

    def finish(self) -> None:
        self._report()

    def _report(self) -> None:
        if self.options.callback is None:
            return
        total = self.options.total
        pct = (self.processed / total * 100.0) if total > 0 else 0.0
        self.options.callback(self.processed, total, pct)


def track(
    iterable: Iterable[T],
    options: ProgressOptions | None = None,
) -> Iterator[T]:
    """Wrap an iterable, reporting progress via options.callback."""
    if options is None:
        options = ProgressOptions()
    state = ProgressState(options=options)
    for item in iterable:
        yield item
        state.advance()
    state.finish()
