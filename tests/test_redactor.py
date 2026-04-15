"""Tests for csvdiff.redactor."""

from __future__ import annotations

import pytest

from csvdiff.differ import DiffResult, FieldChange, RowChange
from csvdiff.redactor import RedactError, RedactOptions, redact_diff


def _fc(f: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=f, old_value=old, new_value=new)


def _change(key, old, new, fcs) -> RowChange:
    return RowChange(key=key, old_row=old, new_row=new, field_changes=fcs)


def make_result(added=None, removed=None, changed=None) -> DiffResult:
    return DiffResult(added=added or [], removed=removed or [], changed=changed or [])


# ---------------------------------------------------------------------------
# RedactOptions validation
# ---------------------------------------------------------------------------

def test_options_empty_columns_raises():
    with pytest.raises(RedactError):
        RedactOptions(columns=set())


def test_options_empty_placeholder_raises():
    with pytest.raises(RedactError):
        RedactOptions(columns={"pw"}, placeholder="")


def test_options_valid():
    opts = RedactOptions(columns={"password"})
    assert opts.placeholder == "***"


# ---------------------------------------------------------------------------
# redact_diff – errors
# ---------------------------------------------------------------------------

def test_redact_none_result_raises():
    with pytest.raises(RedactError):
        redact_diff(None, RedactOptions(columns={"x"}))


def test_redact_none_opts_raises():
    with pytest.raises(RedactError):
        redact_diff(make_result(), None)


# ---------------------------------------------------------------------------
# redact_diff – changed rows
# ---------------------------------------------------------------------------

def test_redact_field_change_value():
    change = _change(
        key=("1",),
        old={"id": "1", "password": "secret"},
        new={"id": "1", "password": "new_secret"},
        fcs=[_fc("password", "secret", "new_secret")],
    )
    result = make_result(changed=[change])
    opts = RedactOptions(columns={"password"})
    out = redact_diff(result, opts)
    fc = out.changed[0].field_changes[0]
    assert fc.old_value == "***"
    assert fc.new_value == "***"


def test_redact_non_sensitive_field_unchanged():
    change = _change(
        key=("1",),
        old={"id": "1", "email": "a@b.com", "name": "alice"},
        new={"id": "1", "email": "x@y.com", "name": "alice"},
        fcs=[_fc("email", "a@b.com", "x@y.com")],
    )
    result = make_result(changed=[change])
    opts = RedactOptions(columns={"password"})
    out = redact_diff(result, opts)
    fc = out.changed[0].field_changes[0]
    assert fc.old_value == "a@b.com"
    assert fc.new_value == "x@y.com"


def test_redact_row_dict_values():
    change = _change(
        key=("1",),
        old={"id": "1", "token": "abc"},
        new={"id": "1", "token": "xyz"},
        fcs=[_fc("token", "abc", "xyz")],
    )
    result = make_result(changed=[change])
    opts = RedactOptions(columns={"token"})
    out = redact_diff(result, opts)
    assert out.changed[0].old_row["token"] == "***"
    assert out.changed[0].new_row["token"] == "***"
    assert out.changed[0].old_row["id"] == "1"


def test_redact_custom_placeholder():
    change = _change(
        key=("1",),
        old={"id": "1", "ssn": "123-45-6789"},
        new={"id": "1", "ssn": "987-65-4321"},
        fcs=[_fc("ssn", "123-45-6789", "987-65-4321")],
    )
    result = make_result(changed=[change])
    opts = RedactOptions(columns={"ssn"}, placeholder="[REDACTED]")
    out = redact_diff(result, opts)
    assert out.changed[0].field_changes[0].old_value == "[REDACTED]"


# ---------------------------------------------------------------------------
# redact_diff – added / removed rows
# ---------------------------------------------------------------------------

def test_redact_added_rows():
    added = [{"id": "2", "password": "p@ss", "name": "bob"}]
    result = make_result(added=added)
    opts = RedactOptions(columns={"password"})
    out = redact_diff(result, opts)
    assert out.added[0]["password"] == "***"
    assert out.added[0]["name"] == "bob"


def test_redact_removed_rows():
    removed = [{"id": "3", "token": "t0k3n"}]
    result = make_result(removed=removed)
    opts = RedactOptions(columns={"token"})
    out = redact_diff(result, opts)
    assert out.removed[0]["token"] == "***"


def test_redact_empty_result_returns_empty():
    result = make_result()
    opts = RedactOptions(columns={"x"})
    out = redact_diff(result, opts)
    assert out.added == []
    assert out.removed == []
    assert out.changed == []
