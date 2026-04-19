"""Tests for csvdiff.differ_metrics."""
import pytest
from csvdiff.differ import DiffResult, RowChange
from csvdiff.differ_metrics import (
    MetricsError,
    MetricsOptions,
    DiffMetrics,
    collect_metrics,
)


def _fc(field="name", old="a", new="b"):
    from csvdiff.differ import FieldChange
    return FieldChange(field=field, old_value=old, new_value=new)


def make_result(added=None, removed=None, changed=None):
    return DiffResult(
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


def _change(key=("1",)):
    return RowChange(key=key, changes=[_fc()])


# --- MetricsOptions ---

def test_options_default_valid():
    o = MetricsOptions()
    assert o.enabled is True


def test_options_disabled_valid():
    o = MetricsOptions(enabled=False)
    assert o.enabled is False


def test_options_invalid_enabled_raises():
    with pytest.raises(MetricsError):
        MetricsOptions(enabled="yes")  # type: ignore


# --- DiffMetrics.as_dict ---

def test_metrics_as_dict_keys():
    m = DiffMetrics(added=1, removed=2, changed=3, total_changes=6, elapsed_seconds=0.5)
    d = m.as_dict()
    assert set(d.keys()) == {"added", "removed", "changed", "total_changes", "elapsed_seconds"}


# --- collect_metrics ---

def test_collect_metrics_empty_result():
    result, metrics = collect_metrics(lambda: make_result())
    assert metrics is not None
    assert metrics.added == 0
    assert metrics.removed == 0
    assert metrics.changed == 0
    assert metrics.total_changes == 0
    assert metrics.elapsed_seconds >= 0


def test_collect_metrics_counts_correctly():
    r = make_result(
        added=[{"id": "1"}],
        removed=[{"id": "2"}, {"id": "3"}],
        changed=[_change()],
    )
    _, metrics = collect_metrics(lambda: r)
    assert metrics.added == 1
    assert metrics.removed == 2
    assert metrics.changed == 1
    assert metrics.total_changes == 4


def test_collect_metrics_disabled_returns_none():
    opts = MetricsOptions(enabled=False)
    result, metrics = collect_metrics(lambda: make_result(), options=opts)
    assert metrics is None
    assert result is not None


def test_collect_metrics_returns_original_result():
    r = make_result(added=[{"id": "x"}])
    returned, _ = collect_metrics(lambda: r)
    assert returned is r


def test_collect_metrics_elapsed_is_float():
    _, metrics = collect_metrics(lambda: make_result())
    assert isinstance(metrics.elapsed_seconds, float)
