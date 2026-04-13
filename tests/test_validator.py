"""Tests for csvdiff.validator."""

import pytest

from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.validator import (
    ValidationRule,
    ValidationResult,
    validate_diff,
    assert_valid,
    ValidationError,
)


def _fc(fname: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=fname, old_value=old, new_value=new)


def make_result(added=None, removed=None, changed=None) -> DiffResult:
    return DiffResult(
        added=added or [],
        removed=removed or [],
        changed=changed or [],
    )


def make_change(key, fields) -> RowChange:
    return RowChange(key=key, changes=fields)


# ── no violations ────────────────────────────────────────────────────────────

def test_validate_empty_result_passes():
    rule = ValidationRule(max_added=0, max_removed=0, max_changed=0)
    vr = validate_diff(make_result(), rule)
    assert vr.passed
    assert vr.violations == []


# ── max_added ────────────────────────────────────────────────────────────────

def test_validate_max_added_exceeded():
    result = make_result(added=[{"id": "1"}, {"id": "2"}])
    rule = ValidationRule(max_added=1)
    vr = validate_diff(result, rule)
    assert not vr.passed
    assert any("added" in v for v in vr.violations)


def test_validate_max_added_exact_passes():
    result = make_result(added=[{"id": "1"}])
    vr = validate_diff(result, ValidationRule(max_added=1))
    assert vr.passed


# ── max_removed ──────────────────────────────────────────────────────────────

def test_validate_max_removed_exceeded():
    result = make_result(removed=[{"id": "1"}, {"id": "2"}, {"id": "3"}])
    rule = ValidationRule(max_removed=2)
    vr = validate_diff(result, rule)
    assert not vr.passed
    assert any("removed" in v for v in vr.violations)


# ── max_changed ──────────────────────────────────────────────────────────────

def test_validate_max_changed_exceeded():
    changes = [make_change(("1",), [_fc("a", "x", "y")]) for _ in range(5)]
    result = make_result(changed=changes)
    vr = validate_diff(result, ValidationRule(max_changed=3))
    assert not vr.passed


# ── max_change_rate ──────────────────────────────────────────────────────────

def test_validate_change_rate_exceeded():
    result = make_result(added=[{"id": str(i)} for i in range(6)])
    rule = ValidationRule(max_change_rate=0.5)
    vr = validate_diff(result, rule, total_rows=10)
    assert not vr.passed
    assert any("rate" in v for v in vr.violations)


def test_validate_change_rate_zero_total_skipped():
    result = make_result(added=[{"id": "1"}])
    rule = ValidationRule(max_change_rate=0.0)
    vr = validate_diff(result, rule, total_rows=0)
    assert vr.passed


# ── forbidden_fields ─────────────────────────────────────────────────────────

def test_validate_forbidden_field_touched():
    change = make_change(("42",), [_fc("salary", "1000", "2000")])
    result = make_result(changed=[change])
    rule = ValidationRule(forbidden_fields=["salary"])
    vr = validate_diff(result, rule)
    assert not vr.passed
    assert any("salary" in v for v in vr.violations)


def test_validate_forbidden_field_not_touched_passes():
    change = make_change(("42",), [_fc("name", "Alice", "Bob")])
    result = make_result(changed=[change])
    rule = ValidationRule(forbidden_fields=["salary"])
    vr = validate_diff(result, rule)
    assert vr.passed


# ── assert_valid ─────────────────────────────────────────────────────────────

def test_assert_valid_raises_on_violation():
    result = make_result(added=[{"id": "1"}, {"id": "2"}])
    with pytest.raises(ValidationError, match="added"):
        assert_valid(result, ValidationRule(max_added=1))


def test_assert_valid_passes_silently():
    assert_valid(make_result(), ValidationRule(max_added=10))
