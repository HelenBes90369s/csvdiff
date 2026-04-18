"""Timeout wrapper for diff operations."""
from __future__ import annotations

import signal
from dataclasses import dataclass, field
from typing import Callable, TypeVar

from csvdiff.differ import DiffResult

T = TypeVar("T")


class TimeoutError(Exception):
    """Raised when a diff operation exceeds the allowed time."""


@dataclass
class TimeoutOptions:
    seconds: int = 30
    message: str = "diff operation timed out"

    def __post_init__(self) -> None:
        if self.seconds <= 0:
            raise ValueError("seconds must be positive")
        if not self.message.strip():
            raise ValueError("message must not be blank")


def _handler(signum: int, frame: object) -> None:  # pragma: no cover
    raise TimeoutError


def run_with_timeout(
    fn: Callable[[], DiffResult],
    options: TimeoutOptions | None = None,
) -> DiffResult:
    """Run *fn* and raise :class:`TimeoutError` if it exceeds the limit.

    Uses SIGALRM, so this only works on Unix-like systems.
    """
    if fn is None:
        raise TimeoutError("fn must not be None")
    opts = options or TimeoutOptions()

    old_handler = signal.signal(signal.SIGALRM, _handler)
    signal.alarm(opts.seconds)
    try:
        result = fn()
    except TimeoutError:
        raise TimeoutError(opts.message)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
    return result
