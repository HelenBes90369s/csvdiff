"""Tests for csvdiff.masker."""
import pytest
from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.masker import MaskError, MaskOptions, mask_diff, _mask_value


def _fc(field, old, new):
    return FieldChange(field, old, new)


def _change(key, old, new, fcs):
    return RowChange(key=key, old_row=old, new_row=new, field_changes=fcs)


def make_result(added=None, removed=None, changed=None):
    return DiffResult(added=added or [], removed=removed or [], changed=changed or [])


# --- MaskOptions validation ---

def test_options_empty_columns_raises():
    with pytest.raises(MaskError):
        MaskOptions(columns=())


def test_options_negative_prefix_raises():
    with pytest.raises(MaskError):
        MaskOptions(columns=("email",), visible_prefix=-1)


def test_options_empty_char_raises():
    with pytest.raises(MaskError):
        MaskOptions(columns=("email",), char="")


def test_options_valid():
    o = MaskOptions(columns=("email",), visible_prefix=3, visible_suffix=1)
    assert o.visible_prefix == 3


# --- _mask_value ---

def test_mask_value_basic():
    opts = MaskOptions(columns=("x",), visible_prefix=2, visible_suffix=0)
    assert _mask_value("hello", opts) == "he***"


def test_mask_value_with_suffix():
    opts = MaskOptions(columns=("x",), visible_prefix=2, visible_suffix=1)
    assert _mask_value("hello", opts) == "he**o"


def test_mask_value_short_string():
    opts = MaskOptions(columns=("x",), visible_prefix=10)
    assert _mask_value("hi", opts) == "hi"


def test_mask_value_custom_char():
    opts = MaskOptions(columns=("x",), visible_prefix=1, char="#")
    assert _mask_value("abc", opts) == "a##"


# --- mask_diff ---

def test_mask_diff_none_raises():
    opts = MaskOptions(columns=("email",))
    with pytest.raises(MaskError):
        mask_diff(None, opts)


def test_mask_diff_added_rows():
    opts = MaskOptions(columns=("email",), visible_prefix=2)
    result = make_result(added=[{"id": "1", "email": "test@x.com"}])
    out = mask_diff(result, opts)
    assert out.added[0]["email"] == "te********"
    assert out.added[0]["id"] == "1"


def test_mask_diff_removed_rows():
    opts = MaskOptions(columns=("email",), visible_prefix=1)
    result = make_result(removed=[{"id": "2", "email": "ab@cd.com"}])
    out = mask_diff(result, opts)
    assert out.removed[0]["email"].startswith("a")
    assert "@" not in out.removed[0]["email"][1:]


def test_mask_diff_changed_rows_field_changes():
    opts = MaskOptions(columns=("secret",), visible_prefix=0)
    fc = _fc("secret", "abc", "xyz")
    rc = _change("1", {"id": "1", "secret": "abc"}, {"id": "1", "secret": "xyz"}, [fc])
    result = make_result(changed=[rc])
    out = mask_diff(result, opts)
    assert out.changed[0].field_changes[0].old_value == "***"
    assert out.changed[0].field_changes[0].new_value == "***"


def test_mask_diff_unchanged_columns_untouched():
    opts = MaskOptions(columns=("secret",), visible_prefix=1)
    fc = _fc("name", "Alice", "Bob")
    rc = _change("1", {"id": "1", "name": "Alice", "secret": "pass"}, {"id": "1", "name": "Bob", "secret": "pass"}, [fc])
    result = make_result(changed=[rc])
    out = mask_diff(result, opts)
    assert out.changed[0].field_changes[0].old_value == "Alice"
    assert out.changed[0].field_changes[0].new_value == "Bob"


def test_mask_diff_empty_result():
    opts = MaskOptions(columns=("x",))
    result = make_result()
    out = mask_diff(result, opts)
    assert out.added == [] and out.removed == [] and out.changed == []
