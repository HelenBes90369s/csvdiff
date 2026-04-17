"""Freeze a DiffResult into an immutable snapshot dict for caching or audit."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from csvdiff.differ import DiffResult, RowChange
from csvdiff.encoder import _result_to_dict  # reuse existing serialiser


class FreezeError(Exception):
    """Raised when freezing or thawing fails."""


@dataclass(frozen=True)
class FrozenDiff:
    checksum: str
    row_count: int
    payload: str  # JSON string

    def as_dict(self) -> dict[str, Any]:
        return {
            "checksum": self.checksum,
            "row_count": self.row_count,
            "payload": json.loads(self.payload),
        }

    def verify(self) -> bool:
        """Return True if the payload matches the stored checksum.

        Useful for a quick integrity check without raising an exception.
        """
        expected = hashlib.sha256(self.payload.encode()).hexdigest()
        return expected == self.checksum


def freeze_diff(result: DiffResult) -> FrozenDiff:
    """Serialise *result* to a FrozenDiff with a SHA-256 checksum."""
    if result is None:
        raise FreezeError("result must not be None")
    data = _result_to_dict(result)
    payload = json.dumps(data, sort_keys=True)
    checksum = hashlib.sha256(payload.encode()).hexdigest()
    row_count = len(result.added) + len(result.removed) + len(result.changed)
    return FrozenDiff(checksum=checksum, row_count=row_count, payload=payload)


def thaw_diff(frozen: FrozenDiff) -> dict[str, Any]:
    """Deserialise a FrozenDiff back to a plain dict (not a DiffResult)."""
    if frozen is None:
        raise FreezeError("frozen must not be None")
    if not frozen.verify():
        raise FreezeError("checksum mismatch: payload may have been tampered with")
    return json.loads(frozen.payload)


def checksums_match(a: FrozenDiff, b: FrozenDiff) -> bool:
    """Return True when two frozen diffs have identical content."""
    return a.checksum == b.checksum
