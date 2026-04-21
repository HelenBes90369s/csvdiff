"""Semaphore-based concurrency limiter for diff operations."""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Callable, TypeVar

from csvdiff.differ import DiffResult

T = TypeVar("T")


class SemaphoreError(Exception):
    """Raised for semaphore configuration or runtime errors."""


@dataclass
class SemaphoreOptions:
    max_concurrent: int = 4
    timeout: float | None = None  # seconds; None means block indefinitely

    def __post_init__(self) -> None:
        if self.max_concurrent < 1:
            raise SemaphoreError("max_concurrent must be >= 1")
        if self.timeout is not None and self.timeout <= 0:
            raise SemaphoreError("timeout must be > 0 when specified")


@dataclass
class SemaphoreState:
    options: SemaphoreOptions
    _sem: threading.Semaphore = field(init=False)
    _lock: threading.Lock = field(init=False, default_factory=threading.Lock)
    _active: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        self._sem = threading.Semaphore(self.options.max_concurrent)

    @property
    def active(self) -> int:
        with self._lock:
            return self._active

    def run(self, fn: Callable[[], DiffResult]) -> DiffResult:
        """Acquire the semaphore, call *fn*, then release."""
        acquired = self._sem.acquire(timeout=self.options.timeout)  # type: ignore[call-arg]
        if not acquired:
            raise SemaphoreError(
                f"Could not acquire semaphore within {self.options.timeout}s"
            )
        with self._lock:
            self._active += 1
        try:
            return fn()
        finally:
            with self._lock:
                self._active -= 1
            self._sem.release()


def make_semaphore(options: SemaphoreOptions | None = None) -> SemaphoreState:
    """Create a :class:`SemaphoreState` with *options* (or defaults)."""
    if options is None:
        options = SemaphoreOptions()
    return SemaphoreState(options=options)
