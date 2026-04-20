"""Tests for csvdiff.differ_queue."""
import pytest

from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_queue import (
    DiffQueue,
    QueueEntry,
    QueueError,
    QueueOptions,
    dequeue,
    drain,
    enqueue,
)


def _empty_result() -> DiffResult:
    return DiffResult(added=[], removed=[], changed=[])


def _entry(job_id: str = "j1") -> QueueEntry:
    return QueueEntry(job_id=job_id, result=_empty_result())


# ---------------------------------------------------------------------------
# QueueOptions validation
# ---------------------------------------------------------------------------

def test_options_default_valid():
    opts = QueueOptions()
    assert opts.max_size == 0
    assert opts.on_overflow == "drop"


def test_options_negative_max_size_raises():
    with pytest.raises(QueueError, match="max_size"):
        QueueOptions(max_size=-1)


def test_options_invalid_overflow_raises():
    with pytest.raises(QueueError, match="on_overflow"):
        QueueOptions(on_overflow="block")


# ---------------------------------------------------------------------------
# enqueue / dequeue basics
# ---------------------------------------------------------------------------

def test_enqueue_none_queue_raises():
    with pytest.raises(QueueError):
        enqueue(None, _entry())


def test_enqueue_none_entry_raises():
    q = DiffQueue(options=QueueOptions())
    with pytest.raises(QueueError):
        enqueue(q, None)


def test_enqueue_and_dequeue_fifo():
    q = DiffQueue(options=QueueOptions())
    e1 = _entry("a")
    e2 = _entry("b")
    enqueue(q, e1)
    enqueue(q, e2)
    assert dequeue(q).job_id == "a"
    assert dequeue(q).job_id == "b"
    assert dequeue(q) is None


def test_dequeue_none_queue_raises():
    with pytest.raises(QueueError):
        dequeue(None)


def test_dequeue_empty_returns_none():
    q = DiffQueue(options=QueueOptions())
    assert dequeue(q) is None


# ---------------------------------------------------------------------------
# overflow behaviour
# ---------------------------------------------------------------------------

def test_overflow_drop_returns_false():
    q = DiffQueue(options=QueueOptions(max_size=1, on_overflow="drop"))
    assert enqueue(q, _entry("a")) is True
    assert enqueue(q, _entry("b")) is False
    assert q.size() == 1


def test_overflow_raise_raises():
    q = DiffQueue(options=QueueOptions(max_size=1, on_overflow="raise"))
    enqueue(q, _entry("a"))
    with pytest.raises(QueueError, match="full"):
        enqueue(q, _entry("b"))


# ---------------------------------------------------------------------------
# drain
# ---------------------------------------------------------------------------

def test_drain_processes_all_entries():
    q = DiffQueue(options=QueueOptions())
    for i in range(3):
        enqueue(q, _entry(str(i)))
    seen = []
    result = drain(q, lambda e: seen.append(e.job_id))
    assert seen == ["0", "1", "2"]
    assert len(result) == 3
    assert q.is_empty()


def test_drain_none_queue_raises():
    with pytest.raises(QueueError):
        drain(None, lambda e: None)


def test_drain_non_callable_raises():
    q = DiffQueue(options=QueueOptions())
    with pytest.raises(QueueError, match="callable"):
        drain(q, "not_a_function")


def test_drain_empty_queue_returns_empty_list():
    q = DiffQueue(options=QueueOptions())
    result = drain(q, lambda e: None)
    assert result == []


# ---------------------------------------------------------------------------
# QueueEntry.ok
# ---------------------------------------------------------------------------

def test_entry_ok_no_changes():
    e = _entry()
    assert e.ok() is True


def test_entry_ok_with_changes():
    r = DiffResult(added=[{"id": "1"}], removed=[], changed=[])
    e = QueueEntry(job_id="x", result=r)
    assert e.ok() is False
