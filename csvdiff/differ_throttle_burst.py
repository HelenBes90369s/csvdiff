"""Burst-aware throttle: allows a short burst of calls before enforcing a rate limit."""
from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, TypeVar

from csvdiff.differ import DiffResult

T = TypeVar("T")


class BurstThrottleError(Exception):
    """Raised for invalid options or throttle violations."""


@dataclass
class BurstThrottleOptions:
    burst_size: int = 5
    rate_per_second: float = 1.0
    raise_on_exceed: bool = False

    def __post_init__(self) -> None:
        if self.burst_size <= 0:
            raise BurstThrottleError("burst_size must be positive")
        if self.rate_per_second <= 0:
            raise BurstThrottleError("rate_per_second must be positive")


@dataclass
class BurstThrottleState:
    options: BurstThrottleOptions
    _tokens: float = field(init=False)
    _last: float = field(init=False)
    _call_count: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self._tokens = float(self.options.burst_size)
        self._last = time.monotonic()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last
        self._last = now
        self._tokens = min(
            float(self.options.burst_size),
            self._tokens + elapsed * self.options.rate_per_second,
        )

    @property
    def call_count(self) -> int:
        return self._call_count

    def allowed(self) -> bool:
        self._refill()
        if self._tokens >= 1.0:
            self._tokens -= 1.0
            self._call_count += 1
            return True
        return False

    def wait_and_call(self, fn: Callable[[], T]) -> T:
        """Block until a token is available, then call fn."""
        while not self.allowed():
            time.sleep(1.0 / self.options.rate_per_second / 10)
        return fn()


def throttle_burst(
    fn: Callable[[], DiffResult],
    state: BurstThrottleState,
) -> DiffResult:
    """Call fn subject to burst throttle rules."""
    if state.options.raise_on_exceed and not state.allowed():
        raise BurstThrottleError("burst throttle limit exceeded")
    if state.options.raise_on_exceed:
        # token already consumed in allowed() check above — just call
        state._call_count += 0  # already incremented
        return fn()
    return state.wait_and_call(fn)
