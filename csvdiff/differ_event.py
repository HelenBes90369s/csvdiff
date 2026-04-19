"""Event bus for broadcasting diff lifecycle events to registered listeners."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Any
from csvdiff.differ import DiffResult


class EventError(Exception):
    pass


EVENT_NAMES = {"before_diff", "after_diff", "on_error"}


@dataclass
class EventOptions:
    listeners: Dict[str, List[Callable[..., None]]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in self.listeners:
            if name not in EVENT_NAMES:
                raise EventError(f"Unknown event name: {name!r}")
        for name, handlers in self.listeners.items():
            if not isinstance(handlers, list):
                raise EventError(f"Listeners for {name!r} must be a list")
            for h in handlers:
                if not callable(h):
                    raise EventError(f"All listeners must be callable")


@dataclass
class EventState:
    emitted: List[tuple] = field(default_factory=list)

    def record(self, name: str, payload: Any) -> None:
        self.emitted.append((name, payload))


def emit(options: EventOptions, name: str, payload: Any, state: EventState | None = None) -> None:
    if name not in EVENT_NAMES:
        raise EventError(f"Unknown event name: {name!r}")
    for handler in options.listeners.get(name, []):
        handler(payload)
    if state is not None:
        state.record(name, payload)


def run_with_events(
    fn: Callable[[], DiffResult],
    options: EventOptions,
    state: EventState | None = None,
) -> DiffResult:
    if fn is None:
        raise EventError("fn must not be None")
    emit(options, "before_diff", None, state)
    try:
        result = fn()
    except Exception as exc:
        emit(options, "on_error", exc, state)
        raise
    emit(options, "after_diff", result, state)
    return result
