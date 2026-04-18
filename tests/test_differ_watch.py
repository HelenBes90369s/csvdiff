"""Tests for csvdiff.differ_watch."""
import time
import pytest

from csvdiff.differ import DiffResult
from csvdiff.differ_watch import (
    WatchError,
    WatchOptions,
    WatchState,
    watch_diff,
    _digest,
)


def make_result(added=None):
    return DiffResult(added=added or [], removed=[], changed=[])


def test_watch_options_default_valid():
    opts = WatchOptions()
    assert opts.interval == 2.0
    assert opts.max_polls is None


def test_watch_options_zero_interval_raises():
    with pytest.raises(WatchError):
        WatchOptions(interval=0)


def test_watch_options_negative_interval_raises():
    with pytest.raises(WatchError):
        WatchOptions(interval=-1.0)


def test_watch_options_zero_max_polls_raises():
    with pytest.raises(WatchError):
        WatchOptions(max_polls=0)


def test_digest_missing_file_raises(tmp_path):
    with pytest.raises(WatchError):
        _digest(str(tmp_path / "missing.csv"))


def test_digest_stable(tmp_path):
    f = tmp_path / "a.csv"
    f.write_text("id,name\n1,Alice\n")
    assert _digest(str(f)) == _digest(str(f))


def test_digest_changes_with_content(tmp_path):
    f = tmp_path / "a.csv"
    f.write_text("id,name\n1,Alice\n")
    d1 = _digest(str(f))
    f.write_text("id,name\n1,Bob\n")
    d2 = _digest(str(f))
    assert d1 != d2


def test_watch_calls_on_change_initially(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id\n1\n")
    b.write_text("id\n2\n")

    calls = []

    def compute(fa, fb):
        return make_result(added=[{"id": "x"}])

    def on_change(r):
        calls.append(r)

    opts = WatchOptions(interval=0.01, max_polls=1)
    state = watch_diff(str(a), str(b), compute, on_change, opts)
    assert len(calls) >= 1
    assert state.polls == 1


def test_watch_detects_file_change(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id\n1\n")
    b.write_text("id\n2\n")

    calls = []
    poll_count = [0]

    def compute(fa, fb):
        return make_result()

    def on_change(r):
        calls.append(r)
        if poll_count[0] == 0:
            a.write_text("id\n99\n")
        poll_count[0] += 1

    opts = WatchOptions(interval=0.01, max_polls=3)
    state = watch_diff(str(a), str(b), compute, on_change, opts)
    assert state.polls == 3
    assert state.changes_detected >= 1
