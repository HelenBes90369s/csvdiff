"""Tests for csvdiff.sampler."""

from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, FieldChange, RowChange
from csvdiff.sampler import SampleError, SampleOptions, sample_diff


def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def make_change(key: tuple, kind: str = "changed") -> RowChange:
    return RowChange(
        key=key,
        kind=kind,
        row={"id": key[0]},
        changes=[_fc("v", "1", "2")] if kind == "changed" else [],
    )


def make_result(n_added: int = 0, n_removed: int = 0, n_changed: int = 0) -> DiffResult:
    return DiffResult(
        added=[make_change((str(i),), "added") for i in range(n_added)],
        removed=[make_change((str(i),), "removed") for i in range(n_removed)],
        changed=[make_change((str(i),), "changed") for i in range(n_changed)],
    )


def test_sample_options_both_raises():
    with pytest.raises(SampleError):
        SampleOptions(n=5, fraction=0.5)


def test_sample_options_negative_n_raises():
    with pytest.raises(SampleError):
        SampleOptions(n=-1)


def test_sample_options_invalid_fraction_raises():
    with pytest.raises(SampleError):
        SampleOptions(fraction=1.5)


def test_sample_no_opts_returns_all():
    result = make_result(n_added=5, n_removed=5, n_changed=5)
    sampled = sample_diff(result, SampleOptions())
    assert len(sampled.added) == 5
    assert len(sampled.removed) == 5
    assert len(sampled.changed) == 5


def test_sample_n_caps_at_available():
    result = make_result(n_added=3)
    sampled = sample_diff(result, SampleOptions(n=100, seed=0))
    assert len(sampled.added) == 3


def test_sample_n_exact():
    result = make_result(n_changed=20)
    sampled = sample_diff(result, SampleOptions(n=5, seed=42))
    assert len(sampled.changed) == 5


def test_sample_fraction():
    result = make_result(n_added=10, n_removed=10, n_changed=10)
    sampled = sample_diff(result, SampleOptions(fraction=0.5, seed=7))
    assert len(sampled.added) == 5
    assert len(sampled.removed) == 5
    assert len(sampled.changed) == 5


def test_sample_fraction_zero():
    result = make_result(n_added=10)
    sampled = sample_diff(result, SampleOptions(fraction=0.0, seed=0))
    assert len(sampled.added) == 0


def test_sample_empty_buckets():
    result = make_result()
    sampled = sample_diff(result, SampleOptions(n=5, seed=0))
    assert sampled.added == []
    assert sampled.removed == []
    assert sampled.changed == []


def test_sample_is_deterministic():
    result = make_result(n_changed=50)
    s1 = sample_diff(result, SampleOptions(n=10, seed=99))
    s2 = sample_diff(result, SampleOptions(n=10, seed=99))
    assert [c.key for c in s1.changed] == [c.key for c in s2.changed]


def test_original_not_mutated():
    result = make_result(n_added=10)
    sample_diff(result, SampleOptions(n=2, seed=0))
    assert len(result.added) == 10
