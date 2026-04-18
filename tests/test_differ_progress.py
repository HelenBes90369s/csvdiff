"""Tests for csvdiff.differ_progress."""
import pytest
from csvdiff.differ_progress import (
    ProgressError,
    ProgressOptions,
    ProgressState,
    track,
)


def test_options_default_valid():
    opts = ProgressOptions()
    assert opts.total == 0
    assert opts.interval == 0.1
    assert opts.callback is None


def test_options_negative_total_raises():
    with pytest.raises(ProgressError, match="total"):
        ProgressOptions(total=-1)


def test_options_zero_interval_raises():
    with pytest.raises(ProgressError, match="interval"):
        ProgressOptions(interval=0)


def test_options_negative_interval_raises():
    with pytest.raises(ProgressError, match="interval"):
        ProgressOptions(interval=-0.5)


def test_state_advance_increments():
    opts = ProgressOptions(total=10)
    state = ProgressState(options=opts)
    state.advance(3)
    assert state.processed == 3


def test_state_finish_calls_callback():
    calls = []

    def cb(processed, total, pct):
        calls.append((processed, total, pct))

    opts = ProgressOptions(total=5, callback=cb, interval=999)
    state = ProgressState(options=opts)
    state.processed = 5
    state.finish()
    assert len(calls) == 1
    assert calls[0] == (5, 5, 100.0)


def test_state_no_callback_does_not_raise():
    opts = ProgressOptions(total=3)
    state = ProgressState(options=opts)
    state.advance(1)
    state.finish()


def test_track_yields_all_items():
    items = [1, 2, 3, 4, 5]
    result = list(track(items))
    assert result == items


def test_track_reports_progress():
    calls = []

    def cb(processed, total, pct):
        calls.append(processed)

    opts = ProgressOptions(total=3, callback=cb, interval=0.0)
    result = list(track(["a", "b", "c"], options=opts))
    assert result == ["a", "b", "c"]
    # finish() always fires; at least one call expected
    assert calls[-1] == 3


def test_track_zero_total_pct_is_zero():
    reported = []

    def cb(processed, total, pct):
        reported.append(pct)

    opts = ProgressOptions(total=0, callback=cb, interval=0.0)
    list(track([], options=opts))
    assert reported == [0.0]
