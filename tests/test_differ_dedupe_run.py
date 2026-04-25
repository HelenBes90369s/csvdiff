"""Tests for csvdiff.differ_dedupe_run."""
import time
import pytest

from csvdiff.differ_dedupe_run import (
    DedupeRunError,
    DedupeRunOptions,
    DedupeRunState,
)


# ---------------------------------------------------------------------------
# Options validation
# ---------------------------------------------------------------------------

def test_options_default_valid():
    opts = DedupeRunOptions()
    assert opts.window_seconds == 60.0
    assert opts.max_entries == 256


def test_options_zero_window_raises():
    with pytest.raises(DedupeRunError, match="window_seconds"):
        DedupeRunOptions(window_seconds=0)


def test_options_negative_window_raises():
    with pytest.raises(DedupeRunError, match="window_seconds"):
        DedupeRunOptions(window_seconds=-1.0)


def test_options_zero_max_entries_raises():
    with pytest.raises(DedupeRunError, match="max_entries"):
        DedupeRunOptions(max_entries=0)


def test_options_negative_max_entries_raises():
    with pytest.raises(DedupeRunError, match="max_entries"):
        DedupeRunOptions(max_entries=-5)


# ---------------------------------------------------------------------------
# State: basic record / is_duplicate
# ---------------------------------------------------------------------------

def _state(window: float = 60.0, max_entries: int = 256) -> DedupeRunState:
    return DedupeRunState(options=DedupeRunOptions(window_seconds=window, max_entries=max_entries))


def test_new_run_is_not_duplicate():
    s = _state()
    assert s.is_duplicate("a.csv", "b.csv", ("id",)) is False


def test_recorded_run_is_duplicate():
    s = _state()
    s.record("a.csv", "b.csv", ("id",))
    assert s.is_duplicate("a.csv", "b.csv", ("id",)) is True


def test_different_paths_not_duplicate():
    s = _state()
    s.record("a.csv", "b.csv", ("id",))
    assert s.is_duplicate("x.csv", "b.csv", ("id",)) is False


def test_different_keys_not_duplicate():
    s = _state()
    s.record("a.csv", "b.csv", ("id",))
    assert s.is_duplicate("a.csv", "b.csv", ("name",)) is False


def test_key_order_is_normalised():
    s = _state()
    s.record("a.csv", "b.csv", ("z", "a"))
    assert s.is_duplicate("a.csv", "b.csv", ("a", "z")) is True


def test_entry_count_increments():
    s = _state()
    assert s.entry_count == 0
    s.record("a.csv", "b.csv", ("id",))
    assert s.entry_count == 1


def test_clear_resets_state():
    s = _state()
    s.record("a.csv", "b.csv", ("id",))
    s.clear()
    assert s.entry_count == 0
    assert s.is_duplicate("a.csv", "b.csv", ("id",)) is False


# ---------------------------------------------------------------------------
# Expiry
# ---------------------------------------------------------------------------

def test_expired_run_is_not_duplicate(monkeypatch):
    """After the window elapses the entry should be treated as new."""
    now = [0.0]
    monkeypatch.setattr(time, "monotonic", lambda: now[0])

    s = _state(window=1.0)
    s.record("a.csv", "b.csv", ("id",))
    assert s.is_duplicate("a.csv", "b.csv", ("id",)) is True

    now[0] = 2.0  # advance past the window
    assert s.is_duplicate("a.csv", "b.csv", ("id",)) is False


# ---------------------------------------------------------------------------
# Capacity eviction
# ---------------------------------------------------------------------------

def test_oldest_entry_evicted_when_full():
    s = _state(max_entries=2)
    s.record("a.csv", "b.csv", ("id",))
    s.record("c.csv", "d.csv", ("id",))
    # Adding a third should evict the oldest
    s.record("e.csv", "f.csv", ("id",))
    assert s.entry_count == 2
