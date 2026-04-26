"""Fallback strategy for diff operations.

Provides a mechanism to run a primary diff function and, on failure,
fall back to one or more alternative functions in order. Each fallback
can be configured with its own error types to catch and an optional
delay before attempting.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence, Tuple, Type

from csvdiff.differ import DiffResult


class FallbackError(Exception):
    """Raised when all fallback strategies are exhausted."""


@dataclass
class FallbackStep:
    """A single step in a fallback chain.

    Attributes:
        fn: Callable that returns a DiffResult.
        catch: Tuple of exception types this step catches from the *previous* step.
                If empty, this step catches any Exception.
        delay: Seconds to wait before executing this step (default 0).
        label: Optional human-readable name for logging / audit.
    """

    fn: Callable[[], DiffResult]
    catch: Tuple[Type[BaseException], ...] = field(default_factory=tuple)
    delay: float = 0.0
    label: str = ""

    def __post_init__(self) -> None:
        if not callable(self.fn):
            raise FallbackError("fn must be callable")
        if self.delay < 0:
            raise FallbackError("delay must be >= 0")
        if not isinstance(self.catch, tuple):
            raise FallbackError("catch must be a tuple of exception types")
        for exc in self.catch:
            if not (isinstance(exc, type) and issubclass(exc, BaseException)):
                raise FallbackError(
                    f"catch entries must be exception classes, got {exc!r}"
                )


@dataclass
class FallbackResult:
    """Outcome of a fallback chain execution.

    Attributes:
        result: The DiffResult produced by the successful step.
        step_index: Zero-based index of the step that succeeded.
        label: Label of the successful step (may be empty).
        errors: Exceptions caught from earlier steps, in order.
    """

    result: DiffResult
    step_index: int
    label: str
    errors: List[BaseException]

    @property
    def used_fallback(self) -> bool:
        """True when a fallback step (not the primary) succeeded."""
        return self.step_index > 0


def run_with_fallback(
    primary: Callable[[], DiffResult],
    fallbacks: Sequence[FallbackStep],
    *,
    primary_label: str = "primary",
) -> FallbackResult:
    """Execute *primary*, falling back through *fallbacks* on error.

    Args:
        primary: The first function to try.
        fallbacks: Ordered sequence of FallbackStep instances.
        primary_label: Label to attach to the primary step in the result.

    Returns:
        FallbackResult describing which step succeeded.

    Raises:
        FallbackError: If every step raises an exception.
    """
    if primary is None:
        raise FallbackError("primary callable must not be None")
    if fallbacks is None:
        raise FallbackError("fallbacks must not be None")

    errors: List[BaseException] = []

    # Attempt primary
    try:
        result = primary()
        return FallbackResult(
            result=result,
            step_index=0,
            label=primary_label,
            errors=[],
        )
    except Exception as exc:  # noqa: BLE001
        errors.append(exc)

    # Attempt each fallback in order
    for idx, step in enumerate(fallbacks, start=1):
        catch_types = step.catch if step.catch else (Exception,)
        if not isinstance(errors[-1], tuple(catch_types)):
            # The previous error is not one we should handle with this step
            raise FallbackError(
                f"Step {idx} ('{step.label or idx}') does not handle "
                f"{type(errors[-1]).__name__}; aborting fallback chain."
            ) from errors[-1]

        if step.delay > 0:
            time.sleep(step.delay)

        try:
            result = step.fn()
            return FallbackResult(
                result=result,
                step_index=idx,
                label=step.label,
                errors=errors,
            )
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    raise FallbackError(
        f"All {1 + len(fallbacks)} fallback step(s) failed. "
        f"Last error: {errors[-1]!r}"
    ) from errors[-1]
