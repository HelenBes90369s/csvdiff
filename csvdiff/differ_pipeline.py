"""Pipeline: chain multiple diff transforms in sequence."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, List, Any
from csvdiff.differ import DiffResult


class PipelineError(Exception):
    pass


TransformFn = Callable[[DiffResult], DiffResult]


@dataclass
class PipelineOptions:
    steps: List[TransformFn] = field(default_factory=list)
    stop_on_error: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.steps, list):
            raise PipelineError("steps must be a list")
        for i, s in enumerate(self.steps):
            if not callable(s):
                raise PipelineError(f"step {i} is not callable")


@dataclass
class PipelineResult:
    result: DiffResult
    steps_run: int
    errors: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


def run_pipeline(result: DiffResult, options: PipelineOptions) -> PipelineResult:
    """Apply each transform step in order, returning a PipelineResult."""
    if result is None:
        raise PipelineError("result must not be None")
    if options is None:
        raise PipelineError("options must not be None")

    current = result
    errors: List[str] = []
    steps_run = 0

    for i, step in enumerate(options.steps):
        try:
            current = step(current)
            steps_run += 1
        except Exception as exc:  # noqa: BLE001
            msg = f"step {i} ({getattr(step, '__name__', '?')}): {exc}"
            errors.append(msg)
            if options.stop_on_error:
                break
            steps_run += 1

    return PipelineResult(result=current, steps_run=steps_run, errors=errors)
