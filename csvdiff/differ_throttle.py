"""Rate-limiting wrapper for diff operations."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, TypeVar

from csvdiff.differ import DiffResult

T = TypeVar("T")


class ThrottleError(Exception):
    pass


@dataclass
class ThrottleOptions:
    min_interval: float = 1.0  # seconds between calls
    max_calls: int = 0         # 0 = unlimited
    raise_on_limit: bool = False

    def __post_init__(self) -> None:
        if self.min_interval <= 0:
            raise ThrottleError("min_interval must be positive")
        if self.max_calls < 0:
            raise ThrottleError("max_calls must be >= 0")


@dataclass
class ThrottleState:
    options: ThrottleOptions
    _last_call: float = field(default=0.0, init=False)
    _call_count: int = field(default=0, init=False)

    @property
    def call_count(self) -> int:
        return self._call_count

    def ready(self) -> bool:
        if self.options.max_calls and self._call_count >= self.options.max_calls:
            return False
        return (time.monotonic() - self._last_call) >= self.options.min_interval

    def record(self) -> None:
        self._last_call = time.monotonic()
        self._call_count += 1

    def wait(self) -> None:
        elapsed = time.monotonic() - self._last_call
        remaining = self.options.min_interval - elapsed
        if remaining > 0:
            time.sleep(remaining)


def throttled_run(
    fn: Callable[[], DiffResult],
    state: ThrottleState,
) -> DiffResult | None:
    opts = state.options
    if opts.max_calls and state.call_count >= opts.max_calls:
        if opts.raise_on_limit:
            raise ThrottleError(
                f"call limit of {opts.max_calls} reached"
            )
        return None
    state.wait()
    result = fn()
    state.record()
    return result
