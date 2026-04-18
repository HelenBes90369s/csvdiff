"""Retry wrapper for diff operations that may fail transiently."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, TypeVar

from csvdiff.differ import DiffResult

T = TypeVar("T")


class RetryError(Exception):
    """Raised when all retry attempts are exhausted."""


@dataclass
class RetryOptions:
    max_attempts: int = 3
    delay: float = 0.5
    backoff: float = 2.0
    exceptions: tuple = field(default_factory=lambda: (Exception,))

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise RetryError("max_attempts must be >= 1")
        if self.delay < 0:
            raise RetryError("delay must be >= 0")
        if self.backoff < 1.0:
            raise RetryError("backoff must be >= 1.0")


def run_with_retry(
    fn: Callable[[], DiffResult],
    options: RetryOptions | None = None,
    *,
    _sleep: Callable[[float], None] = time.sleep,
) -> DiffResult:
    """Call *fn* up to options.max_attempts times, retrying on transient errors."""
    if fn is None:
        raise RetryError("fn must not be None")
    opts = options or RetryOptions()
    delay = opts.delay
    last_exc: Exception | None = None
    for attempt in range(1, opts.max_attempts + 1):
        try:
            return fn()
        except opts.exceptions as exc:  # type: ignore[misc]
            last_exc = exc
            if attempt < opts.max_attempts:
                _sleep(delay)
                delay *= opts.backoff
    raise RetryError(
        f"All {opts.max_attempts} attempts failed. Last error: {last_exc}"
    ) from last_exc
