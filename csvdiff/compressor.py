"""Compress / decompress a DiffResult for compact storage."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from csvdiff.differ import DiffResult
from csvdiff.encoder import Encoding, encode_diff, decode_diff, EncodeError


class CompressError(Exception):
    """Raised when compression operations fail."""


@dataclass(frozen=True)
class CompressedDiff:
    """Wrapper holding compressed bytes and metadata."""
    encoding: Encoding
    data: str
    original_rows: int

    @property
    def size(self) -> int:
        return len(self.data)


def compress_diff(
    result: DiffResult,
    encoding: Encoding = "zlib+base64",
) -> CompressedDiff:
    """Compress *result* using *encoding*."""
    if result is None:
        raise CompressError("result must not be None")
    try:
        enc = encode_diff(result, encoding)
    except EncodeError as exc:
        raise CompressError(str(exc)) from exc
    total = len(result.added) + len(result.removed) + len(result.changed)
    return CompressedDiff(encoding=enc.encoding, data=enc.data, original_rows=total)


def decompress_diff(compressed: CompressedDiff) -> DiffResult:
    """Restore a DiffResult from a CompressedDiff."""
    if compressed is None:
        raise CompressError("compressed must not be None")
    from csvdiff.encoder import EncodedDiff
    try:
        return decode_diff(EncodedDiff(encoding=compressed.encoding, data=compressed.data))
    except EncodeError as exc:
        raise CompressError(str(exc)) from exc


def compression_ratio(compressed: CompressedDiff, result: DiffResult) -> Optional[float]:
    """Return ratio of compressed size to json size (lower is better)."""
    if result is None or compressed is None:
        return None
    baseline = encode_diff(result, "json")
    if len(baseline.data) == 0:
        return None
    return compressed.size / len(baseline.data)
