"""Execution tracer for diff pipeline steps."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from csvdiff.differ import DiffResult


class TracerError(Exception):
    """Raised when tracing configuration or execution fails."""


@dataclass
class TracerOptions:
    enabled: bool = True
    max_spans: int = 200

    def __post_init__(self) -> None:
        if self.max_spans < 1:
            raise TracerError("max_spans must be at least 1")


@dataclass
class Span:
    name: str
    start: float
    end: float
    ok: bool
    error: Optional[str] = None

    @property
    def duration_ms(self) -> float:
        return (self.end - self.start) * 1000.0

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "duration_ms": round(self.duration_ms, 3),
            "ok": self.ok,
            "error": self.error,
        }


@dataclass
class TraceResult:
    spans: List[Span] = field(default_factory=list)
    result: Optional[DiffResult] = None

    @property
    def total_ms(self) -> float:
        return sum(s.duration_ms for s in self.spans)

    def as_dict(self) -> dict:
        return {
            "total_ms": round(self.total_ms, 3),
            "span_count": len(self.spans),
            "spans": [s.as_dict() for s in self.spans],
        }


def trace_pipeline(
    result: DiffResult,
    steps: List[tuple[str, Callable[[DiffResult], DiffResult]]],
    options: Optional[TracerOptions] = None,
) -> TraceResult:
    """Run *steps* sequentially, recording a Span for each."""
    if result None:
        raise TracerError("result must not be None")
    if steps is None:
        raise TracerError("steps must not be None")
    opts = options or TracerOptions()
    spans: List[Span] = []
    current = result
    for name, fn in steps:
        if len(spans) >= opts.max_spans:
            raise TracerError(f"max_spans limit ({opts.max_spans}) exceeded")
        t0 = time.monotonic()
        err: Optional[str] = None
        ok = True
        try:
            current = fn(current)
        except Exception as exc:  # noqa: BLE001
            ok = False
            err = str(exc)
            t1 = time.monotonic()
            spans.append(Span(name=name, start=t0, end=t1, ok=ok, error=err))
            if not opts.enabled:
                raise
            break
        t1 = time.monotonic()
        spans.append(Span(name=name, start=t0, end=t1, ok=ok, error=err))
    return TraceResult(spans=spans, result=current)
