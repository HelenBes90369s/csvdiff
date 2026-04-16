"""Tests for csvdiff.compressor."""
import pytest
from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.compressor import CompressError, CompressedDiff, compress_diff, decompress_diff, compression_ratio


def _fc(field, old, new):
    return FieldChange(field=field, old_value=old, new_value=new)


def _change(key, kind="changed", old=None, new=None, changes=()):
    return RowChange(key=tuple(key), kind=kind, old_row=old or {}, new_row=new or {}, changes=list(changes))


def make_result(**kw):
    return DiffResult(added=kw.get("added", []), removed=kw.get("removed", []), changed=kw.get("changed", []))


def test_compress_none_raises():
    with pytest.raises(CompressError):
        compress_diff(None)


def test_decompress_none_raises():
    with pytest.raises(CompressError):
        decompress_diff(None)


def test_compress_empty_result():
    r = make_result()
    c = compress_diff(r)
    assert isinstance(c, CompressedDiff)
    assert c.original_rows == 0
    assert c.encoding == "zlib+base64"


def test_compress_counts_rows():
    r = make_result(
        added=[_change(("1",), kind="added", new={"id": "1"})],
        removed=[_change(("2",), kind="removed", old={"id": "2"})],
        changed=[_change(("3",), old={"id": "3", "v": "a"}, new={"id": "3", "v": "b"})],
    )
    c = compress_diff(r)
    assert c.original_rows == 3


def test_roundtrip_default_encoding():
    r = make_result(
        changed=[_change(("x",), old={"id": "x", "col": "foo"}, new={"id": "x", "col": "bar"}, changes=[_fc("col", "foo", "bar")])],
    )
    c = compress_diff(r)
    out = decompress_diff(c)
    assert len(out.changed) == 1
    assert out.changed[0].changes[0].new_value == "bar"


def test_roundtrip_base64_encoding():
    r = make_result(added=[_change(("a",), kind="added", new={"id": "a"})])
    c = compress_diff(r, encoding="base64")
    assert c.encoding == "base64"
    out = decompress_diff(c)
    assert len(out.added) == 1


def test_compression_ratio_less_than_one_for_large_input():
    rows = [_change((str(i),), kind="added", new={"id": str(i), "data": "x" * 80}) for i in range(50)]
    r = make_result(added=rows)
    c = compress_diff(r, "zlib+base64")
    ratio = compression_ratio(c, r)
    assert ratio is not None
    assert ratio < 1.0


def test_compression_ratio_none_on_none_result():
    r = make_result()
    c = compress_diff(r)
    assert compression_ratio(c, None) is None


def test_compressed_diff_size_property():
    r = make_result(added=[_change(("1",), kind="added", new={"id": "1"})])
    c = compress_diff(r)
    assert c.size == len(c.data)
