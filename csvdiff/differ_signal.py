"""Signal/callback system for diff lifecycle events."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Any

from csvdiff.differ import DiffResult


class SignalError(Exception):
    """Raised when signal configuration or dispatch fails."""


KNOWN_SIGNALS = ("pre_diff", "post_diff", "on_error", "on_empty", "on_changed")


@dataclass
class SignalOptions:
    handlers: Dict[str, List[Callable]] = field(default_factory=dict)
    stop_on_error: bool = False

    def __post_init__(self) -> None:
        unknown = set(self.handlers) - set(KNOWN_SIGNALS)
        if unknown:
            raise SignalError(f"Unknown signals: {sorted(unknown)}")
        for sig, listeners in self.handlers.items():
            if not isinstance(listeners, list):
                raise SignalError(f"Handlers for '{sig}' must be a list")
            for fn in listeners:
                if not callable(fn):
                    raise SignalError(
                        f"All handlers for '{sig}' must be callable"
                    )


@dataclass
class SignalState:
    options: SignalOptions
    _fired: Dict[str, List[Any]] = field(default_factory=dict)

    def fired(self, signal: str) -> List[Any]:
        """Return list of return values from handlers fired for *signal*."""
        return self._fired.get(signal, [])

    def fire(self, signal: str, payload: Any = None) -> None:
        """Invoke all handlers registered for *signal* with *payload*."""
        if signal not in KNOWN_SIGNALS:
            raise SignalError(f"Unknown signal: '{signal}'")
        results: List[Any] = []
        for fn in self.options.handlers.get(signal, []):
            try:
                results.append(fn(payload))
            except Exception as exc:  # noqa: BLE001
                if self.options.stop_on_error:
                    raise SignalError(
                        f"Handler for '{signal}' raised: {exc}"
                    ) from exc
        self._fired.setdefault(signal, []).extend(results)


def emit_diff_signals(
    state: SignalState,
    result: DiffResult,
    error: Exception | None = None,
) -> DiffResult:
    """Fire lifecycle signals around a completed diff result."""
    if state is None:
        raise SignalError("state must not be None")
    if error is not None:
        state.fire("on_error", error)
        return result
    state.fire("post_diff", result)
    has_changes = bool(
        result.added or result.removed or result.changed
    )
    if not has_changes:
        state.fire("on_empty", result)
    else:
        state.fire("on_changed", result)
    return result
