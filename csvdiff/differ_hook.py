"""Lifecycle hooks for diff operations."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, List, Optional
from csvdiff.differ import DiffResult


class HookError(Exception):
    pass


HookFn = Callable[[DiffResult], None]


@dataclass
class HookOptions:
    before: List[HookFn] = field(default_factory=list)
    after: List[HookFn] = field(default_factory=list)
    on_error: Optional[Callable[[Exception], None]] = None

    def __post_init__(self) -> None:
        if not isinstance(self.before, list):
            raise HookError("before must be a list")
        if not isinstance(self.after, list):
            raise HookError("after must be a list")


@dataclass
class HookState:
    before_calls: int = 0
    after_calls: int = 0
    errors: List[Exception] = field(default_factory=list)


def run_hooks(
    result: DiffResult,
    options: HookOptions,
    *,
    phase: str = "after",
) -> HookState:
    if result is None:
        raise HookError("result must not be None")
    if options is None:
        raise HookError("options must not be None")
    if phase not in ("before", "after"):
        raise HookError(f"unknown phase: {phase!r}")

    state = HookState()
    hooks = options.before if phase == "before" else options.after
    for fn in hooks:
        try:
            fn(result)
            if phase == "before":
                state.before_calls += 1
            else:
                state.after_calls += 1
        except Exception as exc:
            state.errors.append(exc)
            if options.on_error:
                options.on_error(exc)
    return state


def run_with_hooks(
    fn: Callable[[], DiffResult],
    options: HookOptions,
) -> DiffResult:
    if fn is None:
        raise HookError("fn must not be None")
    if options is None:
        raise HookError("options must not be None")
    dummy = DiffResult(added=[], removed=[], changed=[])
    run_hooks(dummy, options, phase="before")
    result = fn()
    run_hooks(result, options, phase="after")
    return result
