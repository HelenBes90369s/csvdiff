"""Tests for csvdiff.differ_tracer."""
from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_tracer import (
    Span,
    TracerError,
    TracerOptions,
    TraceResult,
    trace_pipeline,
)


def _empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


# ---------------------------------------------------------------------------
# TracerOptions
# ---------------------------------------------------------------------------

def test_options_default_valid():
    opts = TracerOptions()
    assert opts.enabled is True
    assert opts.max_spans == 200


def test_options_zero_max_spans_raises():
    with pytest.raises(TracerError):
        TracerOptions(max_spans=0)


def test_options_negative_max_spans_raises():
    with pytest.raises(TracerError):
        TracerOptions(max_spans=-1)


# ---------------------------------------------------------------------------
# Span
# ---------------------------------------------------------------------------

def test_span_duration_ms():
    s = Span(name="step", start=1.0, end=1.5, ok=True)
    assert abs(s.duration_ms - 500.0) < 0.001


def test_span_as_dict_keys():
    s = Span(name="x", start=0.0, end=0.001, ok=True)
    d = s.as_dict()
    assert set(d.keys()) == {"name", "duration_ms", "ok", "error"}
    assert d["name"] == "x"
    assert d["ok"] is True
    assert d["error"] is None


# ---------------------------------------------------------------------------
# TraceResult
# ---------------------------------------------------------------------------

def test_trace_result_total_ms():
    spans = [
        Span("a", 0.0, 0.1, True),
        Span("b", 0.1, 0.3, True),
    ]
    tr = TraceResult(spans=spans)
    assert abs(tr.total_ms - 300.0) < 1.0


def test_trace_result_as_dict():
    tr = TraceResult(spans=[])
    d = tr.as_dict()
    assert d["span_count"] == 0
    assert d["spans"] == []


# ---------------------------------------------------------------------------
# trace_pipeline
# ---------------------------------------------------------------------------

def test_trace_pipeline_none_result_raises():
    with pytest.raises(TracerError):
        trace_pipeline(None, [])


def test_trace_pipeline_none_steps_raises():
    with pytest.raises(TracerError):
        trace_pipeline(_empty_result(), None)


def test_trace_pipeline_empty_steps():
    r = _empty_result()
    tr = trace_pipeline(r, [])
    assert tr.spans == []
    assert tr.result is r


def test_trace_pipeline_records_span_per_step():
    identity = lambda res: res  # noqa: E731
    r = _empty_result()
    tr = trace_pipeline(r, [("step1", identity), ("step2", identity)])
    assert len(tr.spans) == 2
    assert tr.spans[0].name == "step1"
    assert tr.spans[1].name == "step2"


def test_trace_pipeline_all_spans_ok_on_success():
    r = _empty_result()
    tr = trace_pipeline(r, [("a", lambda x: x), ("b", lambda x: x)])
    assert all(s.ok for s in tr.spans)


def test_trace_pipeline_captures_error_span():
    def _boom(res: DiffResult) -> DiffResult:
        raise ValueError("exploded")

    r = _empty_result()
    opts = TracerOptions(enabled=True)
    tr = trace_pipeline(r, [("ok_step", lambda x: x), ("bad_step", _boom)], opts)
    assert len(tr.spans) == 2
    bad = tr.spans[1]
    assert bad.ok is False
    assert "exploded" in bad.error


def test_trace_pipeline_max_spans_exceeded_raises():
    opts = TracerOptions(max_spans=2)
    steps = [(f"s{i}", lambda x: x) for i in range(3)]
    with pytest.raises(TracerError, match="max_spans"):
        trace_pipeline(_empty_result(), steps, opts)


def test_trace_pipeline_result_is_transformed():
    def _add_row(res: DiffResult) -> DiffResult:
        from csvdiff.differ import RowChange
        return DiffResult(
            added=[{"id": "1"}],
            removed=res.removed,
            changed=res.changed,
        )

    r = _empty_result()
    tr = trace_pipeline(r, [("add", _add_row)])
    assert tr.result.added == [{"id": "1"}]
