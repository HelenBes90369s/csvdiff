"""Tests for csvdiff.differ_pipeline."""
import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_pipeline import (
    PipelineError,
    PipelineOptions,
    PipelineResult,
    run_pipeline,
)


def _empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


def _identity(r: DiffResult) -> DiffResult:
    return r


def _boom(r: DiffResult) -> DiffResult:
    raise ValueError("boom")


def test_options_default_valid():
    opts = PipelineOptions()
    assert opts.steps == []
    assert opts.stop_on_error is True


def test_options_non_list_steps_raises():
    with pytest.raises(PipelineError):
        PipelineOptions(steps="bad")  # type: ignore


def test_options_non_callable_step_raises():
    with pytest.raises(PipelineError):
        PipelineOptions(steps=[42])  # type: ignore


def test_run_pipeline_none_result_raises():
    opts = PipelineOptions()
    with pytest.raises(PipelineError):
        run_pipeline(None, opts)  # type: ignore


def test_run_pipeline_none_options_raises():
    with pytest.raises(PipelineError):
        run_pipeline(_empty_result(), None)  # type: ignore


def test_run_pipeline_no_steps():
    r = _empty_result()
    pr = run_pipeline(r, PipelineOptions())
    assert pr.ok
    assert pr.steps_run == 0
    assert pr.result is r


def test_run_pipeline_identity_step():
    r = _empty_result()
    pr = run_pipeline(r, PipelineOptions(steps=[_identity]))
    assert pr.ok
    assert pr.steps_run == 1


def test_run_pipeline_stop_on_error_default():
    calls = []

    def second(r: DiffResult) -> DiffResult:
        calls.append(1)
        return r

    pr = run_pipeline(_empty_result(), PipelineOptions(steps=[_boom, second]))
    assert not pr.ok
    assert len(pr.errors) == 1
    assert "boom" in pr.errors[0]
    assert calls == []  # second step not reached


def test_run_pipeline_continue_on_error():
    calls = []

    def second(r: DiffResult) -> DiffResult:
        calls.append(1)
        return r

    opts = PipelineOptions(steps=[_boom, second], stop_on_error=False)
    pr = run_pipeline(_empty_result(), opts)
    assert not pr.ok
    assert pr.steps_run == 2
    assert calls == [1]


def test_run_pipeline_multiple_steps_applied_in_order():
    log: list = []

    def make_step(n):
        def step(r):
            log.append(n)
            return r
        step.__name__ = f"step{n}"
        return step

    opts = PipelineOptions(steps=[make_step(1), make_step(2), make_step(3)])
    pr = run_pipeline(_empty_result(), opts)
    assert pr.ok
    assert log == [1, 2, 3]
    assert pr.steps_run == 3
