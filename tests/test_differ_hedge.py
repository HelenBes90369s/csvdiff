"""Tests for csvdiff.differ_hedge."""
from __future__ import annotations

import time
import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_hedge import (
    HedgeError,
    HedgeOptions,
    HedgeResult,
    run_hedged,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


def _fast(value: DiffResult):
    """Return a zero-delay callable that returns *value*."""
    def _fn() -> DiffResult:
        return value
    return _fn


def _slow(delay: float, value: DiffResult):
    """Return a callable that sleeps *delay* seconds then returns *value*."""
    def _fn() -> DiffResult:
        time.sleep(delay)
        return value
    return _fn


def _boom():
    """Return a callable that always raises."""
    def _fn() -> DiffResult:
        raise RuntimeError("boom")
    return _fn


# ---------------------------------------------------------------------------
# HedgeOptions validation
# ---------------------------------------------------------------------------

def test_options_default_valid():
    opts = HedgeOptions()
    assert opts.hedge_after == 0.5
    assert opts.timeout == 30.0
    assert opts.label == "hedge"


def test_options_zero_hedge_after_raises():
    with pytest.raises(HedgeError, match="hedge_after"):
        HedgeOptions(hedge_after=0)


def test_options_negative_hedge_after_raises():
    with pytest.raises(HedgeError, match="hedge_after"):
        HedgeOptions(hedge_after=-1.0)


def test_options_zero_timeout_raises():
    with pytest.raises(HedgeError, match="timeout"):
        HedgeOptions(timeout=0)


def test_options_hedge_after_gte_timeout_raises():
    with pytest.raises(HedgeError, match="hedge_after must be less than timeout"):
        HedgeOptions(hedge_after=5.0, timeout=5.0)


def test_options_blank_label_raises():
    with pytest.raises(HedgeError, match="label"):
        HedgeOptions(label="   ")


# ---------------------------------------------------------------------------
# run_hedged — argument validation
# ---------------------------------------------------------------------------

def test_run_hedged_none_primary_raises():
    with pytest.raises(HedgeError, match="primary"):
        run_hedged(None, _fast(_empty_result()))


def test_run_hedged_none_secondary_raises():
    with pytest.raises(HedgeError, match="primary"):
        run_hedged(None, None)


# ---------------------------------------------------------------------------
# run_hedged — fast primary wins without hedging
# ---------------------------------------------------------------------------

def test_primary_wins_no_hedge():
    r = _empty_result()
    opts = HedgeOptions(hedge_after=0.3, timeout=5.0)
    result = run_hedged(_fast(r), _slow(2.0, _empty_result()), opts)
    assert isinstance(result, HedgeResult)
    assert result.winner == "primary"
    assert result.used_hedge is False
    assert result.result is r
    assert result.ok


# ---------------------------------------------------------------------------
# run_hedged — slow primary, secondary wins
# ---------------------------------------------------------------------------

def test_secondary_wins_when_primary_slow():
    r_secondary = _empty_result()
    opts = HedgeOptions(hedge_after=0.05, timeout=5.0)
    result = run_hedged(
        _slow(2.0, _empty_result()),
        _fast(r_secondary),
        opts,
    )
    assert result.winner == "secondary"
    assert result.used_hedge is True
    assert result.result is r_secondary
    assert result.label == "hedge"


# ---------------------------------------------------------------------------
# run_hedged — label propagated
# ---------------------------------------------------------------------------

def test_label_propagated():
    opts = HedgeOptions(hedge_after=0.05, timeout=5.0, label="my-hedge")
    result = run_hedged(_fast(_empty_result()), _fast(_empty_result()), opts)
    assert result.label == "my-hedge"


# ---------------------------------------------------------------------------
# run_hedged — elapsed is non-negative
# ---------------------------------------------------------------------------

def test_elapsed_is_non_negative():
    opts = HedgeOptions(hedge_after=0.3, timeout=5.0)
    result = run_hedged(_fast(_empty_result()), _fast(_empty_result()), opts)
    assert result.elapsed >= 0.0
