"""Circuit-breaker wrapper for diff operations.

Opens the circuit after *threshold* consecutive failures and refuses
further calls until the *reset_timeout* (seconds) has elapsed.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, TypeVar

from csvdiff.differ import DiffResult

T = TypeVar("T")


class CircuitError(Exception):
    """Raised for configuration errors or when the circuit is open."""


@dataclass
class CircuitOptions:
    threshold: int = 3
    reset_timeout: float = 60.0
    half_open_calls: int = 1

    def __post_init__(self) -> None:
        if self.threshold < 1:
            raise CircuitError("threshold must be >= 1")
        if self.reset_timeout <= 0:
            raise CircuitError("reset_timeout must be > 0")
        if self.half_open_calls < 1:
            raise CircuitError("half_open_calls must be >= 1")


_STATE_CLOSED = "closed"
_STATE_OPEN = "open"
_STATE_HALF_OPEN = "half_open"


@dataclass
class CircuitState:
    options: CircuitOptions
    _state: str = field(default=_STATE_CLOSED, init=False)
    _failures: int = field(default=0, init=False)
    _opened_at: float = field(default=0.0, init=False)
    _half_open_successes: int = field(default=0, init=False)

    @property
    def state(self) -> str:
        if self._state == _STATE_OPEN:
            if time.monotonic() - self._opened_at >= self.options.reset_timeout:
                self._state = _STATE_HALF_OPEN
                self._half_open_successes = 0
        return self._state

    def record_success(self) -> None:
        if self._state == _STATE_HALF_OPEN:
            self._half_open_successes += 1
            if self._half_open_successes >= self.options.half_open_calls:
                self._state = _STATE_CLOSED
                self._failures = 0
        else:
            self._failures = 0

    def record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self.options.threshold:
            self._state = _STATE_OPEN
            self._opened_at = time.monotonic()


def run_with_circuit(
    fn: Callable[[], DiffResult],
    state: CircuitState,
) -> DiffResult:
    """Call *fn* through the circuit breaker described by *state*."""
    current = state.state
    if current == _STATE_OPEN:
        raise CircuitError("circuit is open; refusing call")
    try:
        result = fn()
        state.record_success()
        return result
    except Exception:
        state.record_failure()
        raise
