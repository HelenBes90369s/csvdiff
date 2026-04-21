"""Replay a recorded DiffResult through a sequence of transformations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from csvdiff.differ import DiffResult


class ReplayError(Exception):
    """Raised when replay configuration or execution fails."""


@dataclass
class ReplayOptions:
    steps: List[Callable[[DiffResult], DiffResult]] = field(default_factory=list)
    stop_on_error: bool = True
    label: str = "replay"

    def __post_init__(self) -> None:
        if not isinstance(self.steps, list):
            raise ReplayError("steps must be a list")
        for i, s in enumerate(self.steps):
            if not callable(s):
                raise ReplayError(f"step[{i}] is not callable")
        if not self.label or not self.label.strip():
            raise ReplayError("label must not be blank")


@dataclass
class ReplayRecord:
    step_index: int
    step_name: str
    ok: bool
    error: Optional[str] = None


@dataclass
class ReplayResult:
    final: DiffResult
    records: List[ReplayRecord] = field(default_factory=list)
    aborted: bool = False

    @property
    def all_ok(self) -> bool:
        return all(r.ok for r in self.records)


def replay_diff(result: DiffResult, opts: ReplayOptions) -> ReplayResult:
    """Run *result* through each step in *opts.steps* in order.

    If *stop_on_error* is True the replay aborts on the first exception;
    otherwise the original result is forwarded unchanged to the next step.
    """
    if result is None:
        raise ReplayError("result must not be None")
    if opts is None:
        raise ReplayError("opts must not be None")

    current = result
    records: List[ReplayRecord] = []

    for idx, step in enumerate(opts.steps):
        name = getattr(step, "__name__", f"step_{idx}")
        try:
            current = step(current)
            records.append(ReplayRecord(step_index=idx, step_name=name, ok=True))
        except Exception as exc:  # noqa: BLE001
            records.append(
                ReplayRecord(step_index=idx, step_name=name, ok=False, error=str(exc))
            )
            if opts.stop_on_error:
                return ReplayResult(final=current, records=records, aborted=True)
            # keep current unchanged and continue

    return ReplayResult(final=current, records=records, aborted=False)
