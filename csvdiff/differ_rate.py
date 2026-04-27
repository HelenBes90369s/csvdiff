"""Rate-limiting wrapper: cap how many diffs can run per time window."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, List

from csvdiff.differ import DiffResult


class RateError(Exception):
    """Raised for rate-limiter configuration or capacity errors."""


@dataclass
class RateOptions:
    max_calls: int = 10
    window_seconds: float = 1.0

    def __post_init__(self) -> None:
        if self.max_calls < 1:
            raise RateError("max_calls must be >= 1")
        if self.window_seconds <= 0:
            raise RateError("window_seconds must be > 0")


@dataclass
class RateState:
    options: RateOptions
    _timestamps: List[float] = field(default_factory=list)

    def _purge_old(self, now: float) -> None:
        cutoff = now - self.options.window_seconds
        self._timestamps = [t for t in self._timestamps if t > cutoff]

    def allowed(self) -> bool:
        now = time.monotonic()
        self._purge_old(now)
        return len(self._timestamps) < self.options.max_calls

    def record(self) -> None:
        self._timestamps.append(time.monotonic())

    @property
    def call_count(self) -> int:
        self._purge_old(time.monotonic())
        return len(self._timestamps)

    @property
    def remaining(self) -> int:
        """Return how many more calls are allowed in the current window."""
        return max(0, self.options.max_calls - self.call_count)

    def reset(self) -> None:
        """Clear all recorded timestamps, fully resetting the rate window."""
        self._timestamps = []


def rate_limited(
    fn: Callable[[], DiffResult],
    state: RateState,
) -> DiffResult:
    """Run *fn* only if the rate limit allows; raise RateError otherwise."""
    if fn is None:
        raise RateError("fn must not be None")
    if state is None:
        raise RateError("state must not be None")
    if not state.allowed():
        raise RateError(
            f"Rate limit exceeded: max {state.options.max_calls} calls "
            f"per {state.options.window_seconds}s"
        )
    state.record()
    return fn()
