"""Debounce repeated diff calls within a time window."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Optional

from csvdiff.differ import DiffResult


class DebounceError(Exception):
    pass


@dataclass
class DebounceOptions:
    window: float = 1.0  # seconds
    max_wait: float = 0.0  # 0 = unlimited

    def __post_init__(self) -> None:
        if self.window <= 0:
            raise DebounceError("window must be positive")
        if self.max_wait < 0:
            raise DebounceError("max_wait must be non-negative")
        if self.max_wait and self.max_wait < self.window:
            raise DebounceError("max_wait must be >= window when set")


@dataclass
class DebounceState:
    options: DebounceOptions
    _last_call: float = field(default=0.0, init=False)
    _first_pending: float = field(default=0.0, init=False)
    _pending: bool = field(default=False, init=False)
    _last_result: Optional[DiffResult] = field(default=None, init=False)

    def should_fire(self, now: Optional[float] = None) -> bool:
        t = now if now is not None else time.monotonic()
        if not self._pending:
            return False
        since_last = t - self._last_call
        if since_last >= self.options.window:
            return True
        if self.options.max_wait:
            waited = t - self._first_pending
            if waited >= self.options.max_wait:
                return True
        return False

    def record_call(self, now: Optional[float] = None) -> None:
        t = now if now is not None else time.monotonic()
        if not self._pending:
            self._first_pending = t
            self._pending = True
        self._last_call = t

    def fire(self, fn: Callable[[], DiffResult], now: Optional[float] = None) -> DiffResult:
        result = fn()
        self._last_result = result
        self._pending = False
        self._first_pending = 0.0
        return result


def debounce_diff(
    fn: Callable[[], DiffResult],
    options: Optional[DebounceOptions] = None,
) -> "DebounceState":
    if options is None:
        options = DebounceOptions()
    return DebounceState(options=options)
