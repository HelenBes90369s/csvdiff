"""Tests for csvdiff.encoder."""
import pytest
from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.encoder import EncodeError, EncodedDiff, encode_diff, decode_diff


def _fc(field: str, old: str, new: str) -> FieldChange:
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key, kind="changed", old=None, new=None, changes=()):
    return RowChange(
        key=tuple(key),
        kind=kind,
        old_row=old or {},
        new_row=new or {},
        changes=list(changes),
    )


def make_result(**kwargs) -> DiffResult:
    return DiffResult(
        added=kwargs.get("added", []),
        removed=kwargs.get("removed", []),
        changed=kwargs.get("changed", []),
    )


def test_encode_none_raises():
    with pytest.raises(EncodeError):
        encode_diff(None)


def test_encode_json_empty():
    r = make_result()
    enc = encode_diff(r, "json")
    assert enc.encoding == "json"
    assert "added" in enc.data


def test_roundtrip_json():
    r = make_result(
        added=[_change(("1",), kind="added", new={"id": "1", "v": "a"})],
        changed=[_change(("2",), old={"id": "2", "v": "x"}, new={"id": "2", "v": "y"}, changes=[_fc("v", "x", "y")])],
    )
    enc = encode_diff(r, "json")
    out = decode_diff(enc)
    assert len(out.added) == 1
    assert len(out.changed) == 1
    assert out.changed[0].changes[0].field == "v"


def test_roundtrip_base64():
    r = make_result(removed=[_change(("3",), kind="removed", old={"id": "3"})])
    enc = encode_diff(r, "base64")
    assert enc.encoding == "base64"
    out = decode_diff(enc)
    assert len(out.removed) == 1
    assert out.removed[0].key == ("3",)


def test_roundtrip_zlib_base64():
    r = make_result(added=[_change((str(i),), kind="added", new={"id": str(i)}) for i in range(20)])
    enc = encode_diff(r, "zlib+base64")
    assert enc.encoding == "zlib+base64"
    out = decode_diff(enc)
    assert len(out.added) == 20


def test_zlib_smaller_than_base64():
    r = make_result(added=[_change((str(i),), kind="added", new={"id": str(i), "val": "x" * 50}) for i in range(30)])
    b64 = encode_diff(r, "base64")
    zb64 = encode_diff(r, "zlib+base64")
    assert len(zb64.data) < len(b64.data)


def test_unknown_encoding_raises():
    with pytest.raises(EncodeError):
        encode_diff(make_result(), "msgpack")  # type: ignore


def test_decode_unknown_encoding_raises():
    enc = EncodedDiff(encoding="msgpack", data="xyz")  # type: ignore
    with pytest.raises(EncodeError):
        decode_diff(enc)


def test_encoded_diff_decode_method():
    r = make_result()
    enc = encode_diff(r, "json")
    out = enc.decode()
    assert isinstance(out, DiffResult)
