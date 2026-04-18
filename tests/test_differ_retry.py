"""Tests for csvdiff.differ_retry."""
from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult
from csvdiff.differ_retry import RetryError, RetryOptions, run_with_retry


def _empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


# ---------------------------------------------------------------------------
# RetryOptions validation
# ---------------------------------------------------------------------------

def test_retry_options_defaults_are_valid():
    opts = RetryOptions()
    assert opts.max_attempts == 3
    assert opts.delay == 0.5
    assert opts.backoff == 2.0


def test_retry_options_zero_attempts_raises():
    with pytest.raises(RetryError):
        RetryOptions(max_attempts=0)


def test_retry_options_negative_delay_raises():
    with pytest.raises(RetryError):
        RetryOptions(delay=-1.0)


def test_retry_options_backoff_below_one_raises():
    with pytest.raises(RetryError):
        RetryOptions(backoff=0.9)


# ---------------------------------------------------------------------------
# run_with_retry behaviour
# ---------------------------------------------------------------------------

def test_run_with_retry_none_fn_raises():
    with pytest.raises(RetryError):
        run_with_retry(None)  # type: ignore[arg-type]


def test_run_with_retry_succeeds_first_attempt():
    result = run_with_retry(_empty_result, RetryOptions(max_attempts=3), _sleep=lambda _: None)
    assert result.added == []


def test_run_with_retry_succeeds_on_second_attempt():
    calls = []

    def flaky() -> DiffResult:
        calls.append(1)
        if len(calls) < 2:
            raise ValueError("transient")
        return _empty_result()

    result = run_with_retry(
        flaky,
        RetryOptions(max_attempts=3, delay=0.0),
        _sleep=lambda _: None,
    )
    assert len(calls) == 2
    assert result.added == []


def test_run_with_retry_exhausts_attempts_raises():
    def always_fails() -> DiffResult:
        raise RuntimeError("boom")

    with pytest.raises(RetryError, match="3 attempts"):
        run_with_retry(
            always_fails,
            RetryOptions(max_attempts=3, delay=0.0),
            _sleep=lambda _: None,
        )


def test_run_with_retry_respects_exception_filter():
    """Only retry on specified exception types; others propagate immediately."""
    calls = []

    def raises_type_error() -> DiffResult:
        calls.append(1)
        raise TypeError("wrong type")

    opts = RetryOptions(max_attempts=3, delay=0.0, exceptions=(ValueError,))
    with pytest.raises(TypeError):
        run_with_retry(raises_type_error, opts, _sleep=lambda _: None)
    assert len(calls) == 1


def test_run_with_retry_backoff_delays_increase():
    delays: list[float] = []

    def always_fails() -> DiffResult:
        raise ValueError("x")

    opts = RetryOptions(max_attempts=4, delay=1.0, backoff=3.0)
    with pytest.raises(RetryError):
        run_with_retry(always_fails, opts, _sleep=delays.append)

    assert len(delays) == 3
    assert delays[0] == pytest.approx(1.0)
    assert delays[1] == pytest.approx(3.0)
    assert delays[2] == pytest.approx(9.0)
