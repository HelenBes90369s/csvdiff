"""Cache diff results to avoid recomputing unchanged inputs."""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from csvdiff.encoder import encode_diff, decode_diff
from csvdiff.differ import DiffResult


class CacheError(Exception):
    pass


@dataclass
class CacheOptions:
    cache_dir: str = ".csvdiff_cache"
    enabled: bool = True

    def __post_init__(self) -> None:
        if not self.cache_dir or not self.cache_dir.strip():
            raise CacheError("cache_dir must not be blank")


def _file_digest(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def cache_key(file_a: str, file_b: str, keys: list[str]) -> str:
    da = _file_digest(file_a)
    db = _file_digest(file_b)
    raw = json.dumps({"a": da, "b": db, "keys": sorted(keys)}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def load_cached(key: str, opts: CacheOptions) -> Optional[DiffResult]:
    path = Path(opts.cache_dir) / f"{key}.json"
    if not path.exists():
        return None
    try:
        return decode_diff(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise CacheError(f"Failed to load cache entry: {exc}") from exc


def save_cached(key: str, result: DiffResult, opts: CacheOptions) -> None:
    os.makedirs(opts.cache_dir, exist_ok=True)
    path = Path(opts.cache_dir) / f"{key}.json"
    try:
        path.write_text(encode_diff(result), encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        raise CacheError(f"Failed to save cache entry: {exc}") from exc


def clear_cache(opts: CacheOptions) -> int:
    removed = 0
    cache_path = Path(opts.cache_dir)
    if not cache_path.exists():
        return 0
    for entry in cache_path.glob("*.json"):
        entry.unlink()
        removed += 1
    return removed
