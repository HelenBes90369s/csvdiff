"""Tests for csvdiff.differ_cache."""
import json
import os
import pytest

from csvdiff.differ import DiffResult, RowChange, FieldChange
from csvdiff.differ_cache import (
    CacheError,
    CacheOptions,
    cache_key,
    load_cached,
    save_cached,
    clear_cache,
)


def _fc(field="name", old="a", new="b"):
    return FieldChange(field=field, old_value=old, new_value=new)


def make_result():
    return DiffResult(
        added=[{"id": "1", "name": "Alice"}],
        removed=[],
        changed=[
            RowChange(key=("2",), field_changes=[_fc()])
        ],
    )


def test_options_blank_dir_raises():
    with pytest.raises(CacheError):
        CacheOptions(cache_dir="   ")


def test_cache_key_deterministic(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id,name\n1,Alice\n")
    b.write_text("id,name\n2,Bob\n")
    k1 = cache_key(str(a), str(b), ["id"])
    k2 = cache_key(str(a), str(b), ["id"])
    assert k1 == k2


def test_cache_key_changes_with_content(tmp_path):
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    a.write_text("id,name\n1,Alice\n")
    b.write_text("id,name\n2,Bob\n")
    k1 = cache_key(str(a), str(b), ["id"])
    a.write_text("id,name\n1,Changed\n")
    k2 = cache_key(str(a), str(b), ["id"])
    assert k1 != k2


def test_load_cached_missing_returns_none(tmp_path):
    opts = CacheOptions(cache_dir=str(tmp_path / "cache"))
    assert load_cached("nonexistent", opts) is None


def test_save_and_load_roundtrip(tmp_path):
    opts = CacheOptions(cache_dir=str(tmp_path / "cache"))
    result = make_result()
    save_cached("testkey", result, opts)
    loaded = load_cached("testkey", opts)
    assert loaded is not None
    assert len(loaded.added) == 1
    assert len(loaded.changed) == 1
    assert loaded.added[0]["name"] == "Alice"


def test_clear_cache_removes_files(tmp_path):
    opts = CacheOptions(cache_dir=str(tmp_path / "cache"))
    result = make_result()
    save_cached("k1", result, opts)
    save_cached("k2", result, opts)
    removed = clear_cache(opts)
    assert removed == 2
    assert load_cached("k1", opts) is None


def test_clear_cache_nonexistent_dir_returns_zero(tmp_path):
    opts = CacheOptions(cache_dir=str(tmp_path / "no_such_dir"))
    assert clear_cache(opts) == 0


def test_save_cached_creates_directory(tmp_path):
    cache_dir = tmp_path / "nested" / "cache"
    opts = CacheOptions(cache_dir=str(cache_dir))
    save_cached("mykey", make_result(), opts)
    assert (cache_dir / "mykey.json").exists()
