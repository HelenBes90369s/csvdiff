"""Route diff results to multiple handlers based on configurable predicates.

Each route pairs a predicate (a callable that inspects a DiffResult and returns
bool) with a handler (a callable that receives the DiffResult).  When
``route_diff`` is called every matching route's handler is invoked; routes are
evaluated in declaration order and, when ``stop_on_first`` is enabled, only the
first matching handler is called.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List

from csvdiff.differ import DiffResult


class RouterError(Exception):
    """Raised when router configuration or routing fails."""


# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------

@dataclass
class RouteRule:
    """A single predicate → handler pair."""

    name: str
    predicate: Callable[[DiffResult], bool]
    handler: Callable[[DiffResult], None]

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise RouterError("RouteRule name must not be blank")
        if not callable(self.predicate):
            raise RouterError(f"Route '{self.name}': predicate must be callable")
        if not callable(self.handler):
            raise RouterError(f"Route '{self.name}': handler must be callable")


@dataclass
class RouterOptions:
    """Configuration for the diff router."""

    rules: List[RouteRule]
    stop_on_first: bool = False
    raise_on_no_match: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.rules, list):
            raise RouterError("rules must be a list")
        if len(self.rules) == 0:
            raise RouterError("RouterOptions requires at least one rule")
        names = [r.name for r in self.rules]
        if len(names) != len(set(names)):
            raise RouterError("Duplicate rule names are not allowed")


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class RouterSummary:
    """Records which rules fired during a ``route_diff`` call."""

    matched: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def any_matched(self) -> bool:
        return len(self.matched) > 0


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def route_diff(
    result: DiffResult,
    options: RouterOptions,
) -> RouterSummary:
    """Evaluate each rule against *result* and invoke matching handlers.

    Parameters
    ----------
    result:
        The diff result to route.
    options:
        Router configuration including rules and behavioural flags.

    Returns
    -------
    RouterSummary
        Which rule names matched and which were skipped.

    Raises
    ------
    RouterError
        If *result* is ``None``, *options* is ``None``, or
        ``raise_on_no_match`` is set and no rule matched.
    """
    if result is None:
        raise RouterError("result must not be None")
    if options is None:
        raise RouterError("options must not be None")

    summary = RouterSummary()

    for rule in options.rules:
        try:
            matched = rule.predicate(result)
        except Exception as exc:  # pragma: no cover
            raise RouterError(
                f"Predicate for rule '{rule.name}' raised an exception: {exc}"
            ) from exc

        if matched:
            summary.matched.append(rule.name)
            try:
                rule.handler(result)
            except Exception as exc:  # pragma: no cover
                raise RouterError(
                    f"Handler for rule '{rule.name}' raised an exception: {exc}"
                ) from exc
            if options.stop_on_first:
                # Mark remaining rules as skipped
                remaining = options.rules[options.rules.index(rule) + 1:]
                summary.skipped.extend(r.name for r in remaining)
                break
        else:
            summary.skipped.append(rule.name)

    if options.raise_on_no_match and not summary.any_matched:
        raise RouterError("No route matched the provided DiffResult")

    return summary
