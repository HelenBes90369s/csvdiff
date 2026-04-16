import json
import pytest

from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.freezer import (
    FreezeError,
    FrozenDiff,
    freeze_diff,
    thaw_diff,
    checksums_match,
)


def _fc(field="name", old="a", new="b"):
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key=("1",), kind="changed"):
    return RowChange(
        key=key,
        kind=kind,
        old_row={"id": "1", "name": "a"} if kind != "added" else {},
        new_row={"id": "1", "name": "b"} if kind != "removed" else {},
        field_changes=[_fc()] if kind == "changed" else [],
    )


def make_result(added=(), removed=(), changed=()):
    return DiffResult(added=list(added), removed=list(removed), changed=list(changed))


def test_freeze_none_raises():
    with pytest.raises(FreezeError):
        freeze_diff(None)


def test_freeze_empty_result():
    r = make_result()
    frozen = freeze_diff(r)
    assert isinstance(frozen, FrozenDiff)
    assert frozen.row_count == 0
    assert len(frozen.checksum) == 64


def test_freeze_row_count():
    r = make_result(
        added=[_change(kind="added")],
        removed=[_change(kind="removed")],
        changed=[_change()],
    )
    frozen = freeze_diff(r)
    assert frozen.row_count == 3


def test_thaw_none_raises():
    with pytest.raises(FreezeError):
        thaw_diff(None)


def test_thaw_returns_dict():
    r = make_result(changed=[_change()])
    frozen = freeze_diff(r)
    data = thaw_diff(frozen)
    assert isinstance(data, dict)
    assert "changed" in data


def test_thaw_detects_tamper():
    r = make_result()
    frozen = freeze_diff(r)
    bad = FrozenDiff(
        checksum="0" * 64,
        row_count=frozen.row_count,
        payload=frozen.payload,
    )
    with pytest.raises(FreezeError, match="checksum mismatch"):
        thaw_diff(bad)


def test_checksums_match_same_result():
    r = make_result(added=[_change(kind="added")])
    a = freeze_diff(r)
    b = freeze_diff(r)
    assert checksums_match(a, b)


def test_checksums_differ_for_different_results():
    r1 = make_result(added=[_change(kind="added")])
    r2 = make_result(removed=[_change(kind="removed")])
    assert not checksums_match(freeze_diff(r1), freeze_diff(r2))


def test_frozen_as_dict_structure():
    r = make_result()
    frozen = freeze_diff(r)
    d = frozen.as_dict()
    assert "checksum" in d
    assert "row_count" in d
    assert "payload" in d
    assert isinstance(d["payload"], dict)
